# Strategy — Latency of UI Scanning (`ui list` / `DebugUIScanner`)

**Status:** **Lever 1 items 1–2 IMPLEMENTED** (batched top-level reads + free
symbol names). Measured result: first `ui list` **~8.2 s → ~2.3 s**
(30 → 11 round-trips, 3.6×), output unchanged; full unit + 9-test parasitic
suites green. Remaining levers (2–4, and Lever 3) are follow-ups. Everything
below is measured against the real binary
(`/home/shalidor/Projects/Projects__Lavender/AncientsGame/build/sdl/AncientsGame`)
under GDB 17.2, at a safe stop, with the default 1-manager / 8-element UI.

**Implementation map (done):**
- `mcp/gdb_frame_controller.py` — added `_console_print(expr)` (one `print {…}`
  round-trip; the MI `-data-evaluate-expression` channel rejects brace-lists).
- `mcp/debug_scanner.py` — `get_table()` now routes through a
  `_build_top_level_table()` hook (default = the old per-field `_eval`, so the
  scene/entity scanners are unchanged); added `_parse_value_array()`.
- `mcp/debug_scanner_ui.py` — `DebugUIScanner` overrides `_build_top_level_
  table()` to read the 24 fields in ~5 round-trips (`_FIELD_GROUPS`: pointers
  and func-ptrs as `void*`, counts as `unsigned int`, enum + `u32[8]` array
  read alone); `_normalize_handler_ptr` now **keeps** the `<symbol>` annotation.
- `mcp_layered/layer_lav_init.py` — `ui_list_driver` parses the name from the
  stored `0xADDR <symbol>` value (zero round-trips); `resolve_function_name`
  is now only a fallback for unannotated addresses.

**Follow-ups (not done):** Lever 1 item 3 (bound the batch fallback), item 4
(session cache — needs a UI-mutation signal the game doesn't currently expose),
Lever 2 (read the bounded pool directly to push toward ~1 s), Lever 3
(investigate the ~200 ms floor).

---

## TL;DR

1. **Every GDB MI round-trip costs a flat ≈ 200 ms in this environment,
   independent of what the command does.** Measured: `read_response=False`
   (write-only) = **0.1 ms**; `read_response=True` (write + read) = **201 ms**,
   and that 201 ms is the same for `1+1`, a memory read, a symbol lookup, and a
   struct read. The cost lives entirely in the *read/wait-for-response* phase.
2. **Therefore total scan latency ≈ (number of GDB commands) × ~200 ms.** The
   `debug_get_ui_scanner(&game)` C *call* is **not** the bottleneck — it takes
   218 ms, only ~16 ms above the flat tax.
3. A nominal `ui list` issues **~30 round-trips → ~8 s**. If the batched
   enrichment falls back to per-position reads, it explodes to **~382
   round-trips → ~79 s** (a **12.7× cliff**).
4. **GDB can batch many r-values into one round-trip via a brace-list
   `{e1, e2, …}` on the *console* channel (`print`/`call`), printing the
   *entire* structure** (confirmed: `print {1,2,3}` → `$1 = {1, 2, 3}`). It does
   **not** work on `-data-evaluate-expression` (rejected), and the elements must
   be **type-homogeneous**. This is the primary lever.
5. **Strategy: collapse round-trips.** (a) batch the 24 top-level field reads
   into ~4 **type-grouped** console brace-lists (24 → ~4); (b) keep the symbol
   annotations the batch already prints, so handler names cost **zero** extra
   round-trips (no per-address re-lookup); (c) cache the table at session scope.
   → first `ui list` **~8 s → ~1 s**, repeat **→ ~0–200 ms**. A separate,
   higher-ceiling workstream is to investigate whether the ~200 ms floor itself
   is reducible.

---

## 1. Measured latency breakdown

Per-command floor (15 samples each, at a safe stop):

| Command | mean | note |
|---|---|---|
| `-data-evaluate-expression 1+1` | 202.0 ms | no memory |
| `-data-evaluate-expression game.tick__timer_u32` | 202.6 ms | memory read |
| `-data-evaluate-expression (void*)0x555555570740` | 202.6 ms | symbol lookup |
| `-data-evaluate-expression &game.scene_manager` | 201.7 ms | struct read |
| `write(read_response=False)` | **0.1 ms** | write-only |
| `write(read_response=True)` | **201.2 ms** | write + read |

→ **The ~200 ms is a flat per-command tax in the read phase, complexity-
independent.** (pygdbmi's unix reader uses `select.select`, which returns the
instant data arrives — so the delay is GDB producing the response, not a poll
sleep in Python. See §5 for the open investigation.)

`ui list` end-to-end (the path is
`DebugUIUtils.refresh()` → `DebugUIScanner.get_scanner()` + `get_table()`,
then the Goal-2 handler-name resolution):

| Component | Round-trips | Wall |
|---|---|---|
| `get_scanner()` (push/pop frame + `set $x = debug_get_ui_scanner(&game)` + final eval) | 5 | ~1.0 s |
| `get_table()` top-level fields (**24** `DEBUG_UI_SCANNER_FIELDS` evals) | 24 | ~4.9 s |
| `get_table()` `_enrich_table` **batched** `call {…}` (1 shot) | 1 | ~0.26 s |
| Goal-2 handler-name resolution (**10** unique addrs, cached) | 10 | ~2.0 s |
| **Nominal `ui list` total** | **~30** | **~8.2 s** |

**Forced fallback** (batch struct parse defeated so `_batch_with_eval_fallback`
runs; 1 manager + 8 elements = 9 positions):

| Component | Round-trips | Wall |
|---|---|---|
| `_enrich_table` fallback: per position `_advance` (≈5) + `_read_post_condition_fields` (17 evals) | ~381 | ~77 s |
| **Forced-fallback `ui list` total** | **~382** | **~79 s** |

**Batch vs fallback = 30 vs 382 round-trips = 12.7×.** The cliff is driven
purely by round-trip count, which confirms the model.

---

## 1b. Confirmed: brace-list batching (the ~200 ms collapse)

GDB evaluates several r-values in **one** command via a brace-list
`{e1, e2, …}`. This is the mechanism the existing `mcp/_batch_call`
(`gdb_frame_controller.py:71`) already uses to advance the scanner in one shot.
Tested against the live target to settle exactly what it can and cannot do:

| Command form | Channel | Result |
|---|---|---|
| `-data-evaluate-expression {1, 2, 3}` | MI eval | **REJECTED** — `Usage: -data-evaluate-expression expression` (same MI quirk as in-GDB ptr subtraction) |
| `print {1, 2, 3}` | console | `$1 = {1, 2, 3}` ✅ **whole structure** |
| `print {(int)1,(int)2,(int)3}` | console | `$2 = {1, 2, 3}` ✅ |
| `print {(void*)a,(void*)b,(void*)c}` | console | `$3 = {0x.., 0x.., 0x..}` ✅ |
| `call {f(), f()}` | console | `$4 = {0, 0}` ✅ (existing `_batch_call` pattern) |
| `print {…7 ptrs…}` / `{…12 func-ptrs…}` (as `void*`) | console | ✅ whole array, length not a limit |
| `print {24 mixed-type fields}` | console | **REJECTED** (empty) — heterogeneous |
| `print {(void*)×24 fields incl. the `u32[8]` array}` | console | **REJECTED** (empty) — the array member is type-incompatible with scalars |

**Findings (answering the "whole vs last" question):**
1. **GDB prints the *entire* `{…}` structure** — every element, not just the
   last. (`$1 = {1, 2, 3}`.)
2. **Console channel only.** `-data-evaluate-expression` rejects brace-lists
   outright; use `-interpreter-exec console "print {…}"` (or `call {…}`).
3. **Elements must be type-homogeneous** — cast each to one type. Mixed-type
   lists are rejected. Length is *not* the limit (12 elements printed fine).
4. **The `u32[8]` qty-array member cannot sit in a scalar brace-list** — read it
   in its own `print` (it prints as `{0, 8, 0, …}`).
5. **Function pointers print with their symbol name for free**
   (`0x… <m_ui_button__clicked_handler__…>`). The current `_normalize_handler_
   ptr` *strips* that annotation, after which Goal-2 re-resolves each address
   (10 extra round-trips). **Keeping the annotation removes those 10 round-trips
   entirely.**
6. Each batched `print {…}` is still **one ~200 ms round-trip** no matter how
   many elements it holds — so N reads in one brace-list = 200 ms, not N×200 ms.
   The existing `_parse_batch_structs`/`_split_struct_array` already parse this
   `$N = {…}` format, so no new parser is needed.

---

## 2. Where the cost comes from (two sources)

1. **The flat ~200 ms tax × command count.** This is the floor. It applies to
   every `-data-evaluate-expression`, every console `set`/`call`, every
   `-stack-*`. It is the same whether the command reads an integer or a whole
   struct. *You pay ~200 ms just for the round-trip.*
2. **The batch-vs-fallback cliff.** `DebugUIScanner._enrich_table` is designed
   to visit every manager + element in **one** batched `call {…}`
   (`mcp/debug_scanner_ui.py:101`, `_batch_call` at `gdb_frame_controller.py:71`).
   That is the whole game: 1 command instead of ~22 per position. But if the
   batch's console output doesn't parse (`_parse_batch_structs`, `:441`), it
   falls back to `_batch_with_eval_fallback` (`:279`) — `_advance` + 17 evals
   *per position* — which re-inflates the count ~12×. So the *variance* in UI
   scan latency is dominated by whether that batch parse succeeds.

The 24 top-level field reads (`DEBUG_UI_SCANNER_FIELDS`, `:35`) are a large,
fixed chunk of the nominal cost (~4.9 s of the ~8.2 s). Two of them are needed
to *drive* the iteration; the rest are read but largely unused by `ui list`.
Either way, §1b shows they collapse into **~4 type-grouped brace-lists** (~0.8 s)
on the console channel — the single biggest, confirmed win.

---

## 3. Strategy (prioritized)

### Lever 1 — Collapse round-trips with type-grouped brace-batching (primary)
Every command dropped saves ~200 ms, and a brace-list reads N values in **one**
command. Rebuild the read path around it (all via the console `print {…}`
channel; `-data-evaluate-expression` can't do braces):

1. **Batch the 24 top-level field reads by type.** Group the
   `DEBUG_UI_SCANNER_FIELDS` into type-homogeneous brace-lists, each one
   `print`:
   - **pointers** (7) → `print {(void*)p_ui_context, (void*)p_ui_manager__
     current, (void*)p_ptr_ui_element__current, (void*)p_ui_element__current,
     (void*)p_parent__current, (void*)p_child__current, (void*)p_next__current}`
   - **function pointers** (12) → `print {(void*)m_next_manager, …, (void*)
     m_ui_dispose_handler__current}` — **also yields the symbol names for free**
   - **ints/uuids** (3) → `print {(int)uuid_of__ui_manager__current, (int)
     uuid_of__ui_element__current, (int)max_quantity_of__ui_managers__u32}`
   - **the `u32[8]` qty-array** (1) → its own `print` (can't share a scalar list)
   → **24 reads → 4 console `print`s (~0.8 s instead of ~4.9 s)**, reusing the
   existing `_split_struct_array` parser on each `$N = {…}`.
2. **Keep the symbol annotations instead of re-resolving.** The batched
   iteration already prints each handler as `0x… <symbol>`. Stop stripping it
   in `_normalize_handler_ptr`; carry the name through. This deletes Goal-2's
   10 `resolve_function_name` round-trips (~2.0 s) **and** the per-addr lookups
   for any future name need. (Keep `resolve_function_name` as a fallback for
   addresses with no annotation.)
3. **Never let the batch fall back.** The `_batch_with_eval_fallback` path is
   the catastrophic 12.7× case. Harden `_parse_batch_structs` so a format
   mismatch degrades *boundedly* (cap positions / bounded direct read), so the
   worst case stays ≈ nominal, not 382 round-trips.
4. **Cache the table at session scope.** Today each `ui list` re-captures from
   scratch. Cache and invalidate only on real UI mutation (add/dispose). A
   repeat `ui list` then re-reads at most the pointer set in **one** brace-list
   to check freshness → **~0–200 ms**.

**Expected result of Lever 1:** first `ui list` **~8.2 s → ~1 s** (4 grouped
reads + C call + batch iteration, names free); repeat **~0–200 ms** (session
cache + one freshness brace-list). Worst case bounded ≈ nominal.

### Lever 2 — Read the pool directly, bypass the iterate-dance (structural)
The scanner's capture-struct-then-batched-cast-and-call design exists to avoid
reading a huge struct. But the UI pool is **bounded** (`MAX_QUANTITY_OF__UI_
MANAGERS = 8` × a small element count). Reading the manager/element pointer and
identity fields **directly** (the same robust recipe the scene tracker uses in
`layer_lav_init._read_active_scene` — separate reads + Python offset math, no
in-GDB pointer subtraction) can replace the capture + batch + parse dance with
a small, fixed, *predictable* number of reads. This also removes the parse-
fragility that creates the fallback cliff. (The same robust recipe is the basis
of the process-pool model in `PLANS/process_trace.md` §1.)

### Lever 3 — Attack the flat ~200 ms tax (separate, higher-ceiling workstream)
The single biggest number is the flat ~200 ms *per command*, which taxes every
tool, not just `ui list`. It is in the read phase and is complexity-independent,
so the usual suspects are GDB-side, not our code:
- GDB config: is `set trace-commands` / a prompt / a large buffer /
  `set trace-off` in play? Confirm the exact GDB invocation + `show` state.
- pygdbmi `IoManager` threading/polling behavior on this Python (3.14) / GDB
  (17.2) combo.
- Whether the inferior's continuous stdout (the `[breakpoint]`/`[scene]`
  prints) is being interlepped/delayed through GDB's relay.

If the floor can be cut from ~200 ms to ~20 ms, **every** debug tool gets ~10×
faster for free — the highest-ceiling win. **Scope it as its own
investigation** (reproducible micro-benchmark: N trivial evals, measure the
floor; then bisect GDB config / pygdbmi path). Do **not** gate the Lever-1 UI
fixes on it.

### Cadence / policy (cheap, high value)
- UI scans already run only at safe stops (correct — keep that).
- Do **not** re-scan UI on every step of a long `step` loop; gate it behind an
  explicit request or a "UI mutated" signal. Re-scanning each frame would
  multiply the ~8 s cost across the whole run.

---

## 4. Concrete before → after (targets)

| Scenario | Today | Target (Lever 1: brace-batching) |
|---|---|---|
| First `ui list` (1 mgr / 8 el) | ~8.2 s (30 rt) | **~1 s** (~5 rt: 4 grouped reads + C call + batch iteration; names free) |
| Repeated `ui list` (unchanged UI) | ~8.2 s each (fresh capture) | **~0–200 ms** (session cache + one freshness brace-list) |
| Batch parse fails (fallback) | ~79 s (382 rt) | bounded ≈ nominal (hardened/bounded degrade) |
| Larger UI (e.g., 8 mgrs, ~100 el) | scales with element count (fallback risk) | ≈ flat (element count grows the *batch*, not the round-trips) |

---

## 5. Open questions / risks

1. **Is the ~200 ms floor reducible?** (Lever 3.) Highest ceiling; needs a
   dedicated, instrumented bisect of GDB config + pygdbmi I/O. Until answered,
   assume it is a fixed cost and optimize around it (Lever 1/2).
2. **Batch-parse fragility.** `_parse_batch_structs` is a regex over GDB's
   printed struct array; a GDB version or verbosity change can silently defeat
   it → the 12.7× cliff. Hardening (Lever 1.1) or switching to the direct pool
   read (Lever 2) removes the dependence.
3. **Cache-invalidation correctness.** A session-level UI cache is only safe if
   it's invalidated on real UI mutation. The `dispose` handler already frees an
   element (`debug_ui_utils.py` sets `self._scanner = None`); a shared cache
   needs an equivalent invalidation hook (or a conservative TTL).
4. **Two write paths, one tax.** The scanner uses `gdbmi.write` (the hooked
   controller write) while `resolve_function_name`/session drivers use
   `GDBSession.write` (`layer_pygdbmi.py:498`, `_orig_write`). Both pay the
   ~200 ms; the split only affects hook processing, not the floor. Any fix to
   the floor (Lever 3) should verify it applies to **both** paths.

---

## 6. Non-goals
- No change to the C `debug_get_ui_scanner` (its real work is ~16 ms above the
  tax — not worth touching for latency).
- No change to what `ui list` *shows* — only how/when it's computed.
- This doc is a strategy; the corresponding code changes are a separate,
  later task (and would be validated against the parasitic suite).
