# `aliased_texture_manager` — Design Review

> **Module:** `core/include/rendering/aliased_texture_manager.h` + `core/source/rendering/aliased_texture_manager.c`
> **Record type:** `Aliased_Texture_Manager` (`core/include/defines.h:858-861`)
> **Embedding:** `Gfx_Context.aliased_texture_manager` (`defines.h:2526`) → `Game`
> **Production consumers:** init — `core/source/rendering/gfx_context.c:20`, `core/source/game.c:105` · uuid lookup — `sdl/source/rendering/opengl/gl_gfx_window.c:118,277`, `sdl/source/rendering/opengl/gl_render_world.c:293`
> **Currently uncalled production APIs:** `allocate_texture_with__alias`, `load_texture_from__path_with__alias`, `get_uuid_of__aliased_texture`, `release_*` (see **C2**)
> **Related documents:**
> - `docs/core/memory/Life_Cycle_Patterns.md` (life cycle / ownership SSOT)
> - `agents/docs/design/memory/Life_Cycle_Patterns.design.md` (post v1.0.0 init/dealloc discipline)
> - `agents/core/design/include/rendering/aliased_texture.design.md` (record-level findings F1–F7)
> - `agents/core/design/design_guide.md` (checklist §1–§10)
> - `agents/core/design/design_pipeline.md` (pass structure, report format)
> - `agents/terminiologies/index.md` (terminology)
>
> **Status:** Under review. **Concerns documented only — no code changes made at
> this time.** Not yet tracked via `track_core_modules.py`.

---

## 1. Module Summary

`aliased_texture_manager` is a **pool-level** module: it owns a fixed
128-slot pool of `Aliased_Texture` records and surfaces a stable semantic —
*name ↔ uuid ↔ texture handle* — to its callers. Callers never touch the pool,
the UUID hashing, or the platform texture functions directly.

- **Layer:** **Rendering** (per `design_guide.md` §1; resolves aliased_texture
  **F9** — the guide now names the layer).
- **Role:** **Abstraction.** It encapsulates the pool, the serialization-header
  UUID scheme, and `PLATFORM_*` texture calls behind alias/uuid operations.
  It is built on two lower abstractions: the `aliased_texture` **record**
  (alias ↔ handle) and the serialization-header pool primitives
  (`serialization/hashing.h`, `serialization/serialization_header.h`).

```c
typedef struct Aliased_Texture_Manager_t {   // defines.h:858
    Aliased_Texture aliased_textures[MAX_QUANTITY_OF__ALIASED_TEXTURES]; // 128
    Repeatable_Psuedo_Random repeatable_psuedo_random_for__texture_uuid;
} Aliased_Texture_Manager;
```

### 1.1 The UUID Representation Invariant (the contract this module must uphold)

The serialization-header scheme encodes the slot address **inside** the uuid:
for an allocated slot `i`, `dehash_identitier_u32_in__contigious_array` recovers
slot `i` from the slot's uuid (`hashing.c:10-46,116-157`). Concretely, uuid
resolution (`hashing.c:86-99`) zeroes the low `log2(capacity)` bits, probes from
slot 0 for the first free slot, and folds that slot index back into the uuid —
so **`uuid % capacity` resolves to the slot's own index**, and the invariant is:

> **Representation Invariant:** for every allocated slot `i`,
> `dehash(slot_i.uuid) == slot_i`.

`allocate_serialization_header_with__uuid_branding` (`hashing.h:138-153`)
establishes this invariant atomically (find free slot `i`, mint uuid with
`uuid % 128 == i`, write it into slot `i`). **Finding F3** is a violation of
this invariant by this module.

### 1.2 Current pipeline state (context for severity)

The alias/uuid texture pipeline is presently **Scaffolding**: the registrar
(`rendering/implemented/aliased_texture_registrar.c:8-15`) has empty
`GEN-BEGIN/GEN-END` blocks, nothing calls the allocate/load/release APIs, and
nothing assigns real values to `Graphics_Window.tile_map__texture__uuid` /
`ui_tile_map__texture__uuid` (initialised to `IDENTIFIER__UNKNOWN__u32` at
`graphics_window.c:30`; the setters have no callers). The only live production
behaviour is: init (twice — **F1**) and uuid lookups that are fed
`IDENTIFIER__UNKNOWN__u32`, which take the failure branch in
`gl_gfx_window.c:118-128` (window disabled). Several findings below are
therefore *latent* rather than *active* — but they are on the critical path
the moment the pipeline is wired up.

---

## 2. Ownership & Life Cycle Model (resolves findings 6.2 / 6.3)

Per `Life_Cycle_Patterns.md`:

| Resource | Owner | Boundary |
|----------|-------|----------|
| `Aliased_Texture` slot | the manager | allocation (`allocate_serialization_header_with__uuid_branding`) and release (`initialize_aliased_texture`) both in this module — create/destroy co-located ✓ |
| `PLATFORM_Texture` handle | the manager (comment at `defines.h:855-857`: "Takes ownership of named textures") | `PLATFORM_allocate_texture*` in / `PLATFORM_release_texture` out, in this module |
| `*p_OUT_texture` (the `Texture` **value** copied out) | **disputed** — see **F6** | `aliased_texture_manager.h:10-11` says *caller does not own*; `Life_Cycle_Patterns.md` §2 says *caller owns* and cites this very function as the example |

### `a > b > c` placement

- `Aliased_Texture_Manager` lives inside `Gfx_Context` inside `Game` →
  **level (a), full game life cycle, implied shared.**
- An individual slot, while allocated, is **level (c)** — single-owner, owned
  by the manager, bounded by the manager's context.

### init/shutdown stack (6.3)

- Init is **not a clean stack**: `initialize_game` initialises the manager
  **twice** (via `initialize_gfx_context` at `game.c:94-95` →
  `gfx_context.c:20-21`, then directly at `game.c:105-106` on the *same*
  object, `game.h:203-206`). See **F1**.
- There is **no shutdown path**: no production code calls
  `release_all_aliased_textures` (test-only). Reclamation currently relies on
  process exit (crash-only). Acceptable for level-(a) resources *only if* the
  release functions are correct when they are eventually used — see **F5**.

---

## 3. Findings Register

Each finding carries the review decision and a timeline. **"Documented (not
acted)"** means: recorded here now, no code change at this time.

| # | Concern | Class | Timeline | Status now |
|:-:|---------|-------|----------|------------|
| **F1** | Double init in `initialize_game`; init not idempotent | Temporal coupling | pre v1.0.0 (remove redundant call) · post v1.0.0 (guard) | Documented (not acted) |
| **F2** | `get_uuid_of__aliased_texture` NULL-derefs on miss | Error boundary / crash | **pre v1.0.0** | Documented (not acted) |
| **F3** | `allocate_texture_with__alias` orphans the slot uuid (Representation Invariant broken); fossil re-init; branding lost, postcondition non-uniform | Correctness | **pre v1.0.0** | Documented (not acted) |
| **F4** | No rollback on failure paths → pool capacity erosion | Ownership / error boundary | pre v1.0.0 | Documented (not acted) |
| **F5** | Release path not viable under the real backend (unconditional release, stale handles, SDL NULL-deref, masked by stub) | Ownership / testing | pre v1.0.0 (policy) · post v1.0.0 (root cause, aliased_texture F1) | Documented (not acted) |
| **F6** | `p_OUT_` ownership contract contradicts the SSOT; optional out-param misnamed | Contract / doc (Mode Confusion) | pre v1.0.0 (doc) | Documented (not acted) |
| **F7** | Path building: fixed-size `memcpy` → source over-read / unterminated destination; no NULL check | Correctness | pre v1.0.0 | Documented (not acted) |
| **F8** | Duplicate aliases → second slot unreachable by alias (Non-Injective; WARNING mischaracterises behaviour) | Correctness / contract | pre v1.0.0 | Documented (not acted) |
| **F9** | Unused `game.h` include in the `.c` (layer violation + unused include) | Dependency direction | pre v1.0.0 | Documented (not acted) |
| **F10** | Test suite: vacuous uuid test, stub-only release test, no round-trip coverage, dangling spec refs | Testing | pre v1.0.0 | Documented (known gap for spec refs) |

---

## 4. Findings Detail

### F1 — Double init in `initialize_game`; init is not idempotent  ·  *pre v1.0.0 (call) / post v1.0.0 (guard)*

`initialize_game` (`game.c:91-106`) runs:

```c
initialize_gfx_context(get_p_gfx_context_from__game(p_game));   // :94
    └─> initialize_aliased_texture_manager(...)                 // gfx_context.c:20
...
initialize_aliased_texture_manager(                             // :105
        get_p_aliased_texture_manager_from__game(p_game));      // = &p_game->gfx_context.aliased_texture_manager
```

The **same object** is initialised twice.

- **Impact today: none.** Manager init is **total**
  (`initialize_serialization_header__contiguous_array` memsets every full
  struct, `serialization_header.c:32-53`), and nothing allocates between the
  two calls (the registrar is an empty stub — **C2**).
- **Latent hazard:** if any texture were allocated in the window between the
  two inits, the second init would wipe the name/uuid bookkeeping while the
  platform handle stays live → **Leak by side effect** (handle unreachable).
  The PRNG is also re-seeded to the *same* value (seed = manager address), so
  the uuid sequence restarts; uuids issued before the reset (and stored
  externally, e.g. in `Graphics_Window.*_tile_map__texture__uuid`) would point
  at wiped slots → **State Desync**.
- `initialize_aliased_texture_manager` is **Partial** where it presents as
  safe to repeat: no double-invocation guard (7.3), no enforced ordering (7.1).

**Decision:** remove the redundant call at `game.c:105-106` **pre v1.0.0**
(one-line fix; `initialize_gfx_context` already owns this step). A
sentinel-checked, **Idempotence**-guardable init belongs to the post v1.0.0
init/dealloc discipline
(`agents/docs/design/memory/Life_Cycle_Patterns.design.md` §2).

### F2 — `get_uuid_of__aliased_texture` NULL-derefs on miss  ·  *pre v1.0.0*

`aliased_texture_manager.c:219-238`: on a missed alias the function logs
`debug_error` — and then **falls through** to

```c
return GET_UUID_P(p_aliased_texture__matching);   // matching == 0
```

`GET_UUID_P(0)` is `((Serialization_Header*)0)->uuid` — a NULL dereference. A
misspelled name, a released texture, or an init-order slip **crashes the
engine** instead of reporting the miss.

- The correct behaviour is pinned by the engine's own SSOT: return the
  **`IDENTIFIER__UNKNOWN__u32` Sentinel**
  (`Life_Cycle_Patterns.md` §3; `is_identifier_u32__invalid`,
  `identifiers.h:46-49`). The test is even *named*
  `aliased_texture_manager__get_uuid_of__aliased_texture__returns_unknown_when_not_found`
  — but its body is `(void)uuid` (see **F10**), so it pins nothing.
- Sibling lookup functions handle the miss correctly (return
  `true`/failure); this one is the outlier in the module's error boundary.

**Decision:** return `IDENTIFIER__UNKNOWN__u32` on miss, **pre v1.0.0**.
Two-line fix; makes the function **Total** over its stated domain.

### F3 — `allocate_texture_with__alias` orphans the slot's uuid  ·  *pre v1.0.0*

The tail of `allocate_texture_with__alias` (`.c:107-115`):

```c
initialize_serialization_header(
        (Serialization_Header*)p_aliased_texture__available,
        get_next_available__random_uuid_in__contiguous_array(
                (Serialization_Header*)p_aliased_texture_manager->aliased_textures,
                MAX_QUANTITY_OF__ALIASED_TEXTURES,
                &p_aliased_texture_manager->repeatable_psuedo_random_for__texture_uuid),
        sizeof(Aliased_Texture));
```

Step by step (capacity 128, free slot `i` is the first free slot from 0):

1. `allocate_serialization_header_with__uuid_branding` (`.c:79-86`,
   `hashing.h:138-153`) finds slot `i` and writes a **branded** uuid `A` with
   `A % 128 == i` — the Representation Invariant (§1.1) holds.
2. The re-init resolves a **new** uuid `B` against an array in which slot `i`
   is *already allocated*. Resolution (`hashing.c:86-99`) probes from slot 0
   for the first free slot — now slot `j ≠ i` — so `B % 128 == j`.
3. `B` is written into slot `i`. `dehash(B)` starts at `j`, finds a free slot,
   and returns **nothing** (`.c:116-157`).

Consequences, for **every** texture created through this function:

- **uuid round-trip broken:** `get_uuid_of__aliased_texture(name)` → `B` →
  `get_texture_by__uuid(B)` → "failed to find texture". The handle is
  reachable by alias only.
- **Branding lost:** `B` is unbranded, contradicting the
  `GET_UUID_BRANDING(Lavender_Type__Aliased_Texture, 0)` passed at allocation.
- **Non-uniform postcondition** between the two supposed-equivalent allocate
  functions: `load_texture_from__path_with__alias` (`.c:119-186`) performs no
  re-init, so its slots keep the valid branded `A` and *do* round-trip.

**Root cause — fossil of a superseded allocation strategy.** The file still
contains the previous strategy's slot search,
`get_p_aliased_texture_thats__available_from__manager` (`.c:39-59`), which is
**dead code** (never called; the live path is the header-allocation call).
Under the *name-scan* strategy, re-init was correct: the scan and the uuid
resolution both return the *first free slot from 0*, so the minted uuid
dehashed to the very slot being filled. When allocation migrated to
`allocate_serialization_header_with__uuid_branding` (which mints and writes the
uuid atomically), the re-init became a **State Desync** — it was left in.
This is also a small **DRY** violation: two "find a free slot" policies in one
file, one dead.

**Decision:** delete the re-init block (`.c:107-115`) and the dead
`get_p_aliased_texture_thats__available_from__manager`, **pre v1.0.0**.
Currently masked by zero production callers (**C2**) and no round-trip test
(**F10**) — it will bite immediately once the pipeline is wired.

### F4 — No rollback on failure: pool capacity erosion  ·  *pre v1.0.0*

Both allocate functions take the slot **first** and fail **after**:

- `allocate_texture_with__alias`: `PLATFORM_allocate_texture` fails (`.c:92-99`)
  → `return true` with the slot already allocated (uuid ≠
  `IDENTIFIER__UNKNOWN__u32`) but **unnamed and untextured**.
- `load_texture_from__path_with__alias`: base-directory overflow (`.c:156-161`)
  or `PLATFORM_allocate_texture_with__path` failure (`.c:168-177`) → same.

Such a zombie slot is invisible to name-based lookups (empty name ⇒
"unused", `aliased_texture.h:46-50`) but **occupies capacity** in the
uuid-allocation sense (header allocated, `poll_for__uuid_collision` treats it
as occupied, `hashing.c:35-40`). Every failed call permanently consumes one of
128 slots: 128 failures exhaust the pool with **zero live textures**. This is
a **Leak by side effect** at the pool level (no handle is leaked — the
platform call failed — but the *address space* is), and it violates 9.3:
mid-operation failure leaves state invalid.

**Decision:** on every failure path after slot allocation,
`DEALLOCATE_P` the slot before returning, **pre v1.0.0**.

### F5 — Release path is not viable under the real backend  ·  *pre v1.0.0 (policy) / post v1.0.0 (root cause)*

`release_all_aliased_textures` (`.c:299-315`) releases **all 128 slots
unconditionally**, regardless of occupancy:

1. **Free slot** → `texture.p_PLATFORM_texture == 0` →
   `SDL_release_texture` (`sdl_texture_manager.c:45-56`) performs pointer
   arithmetic on the NULL handle (`p - p_SDL_texture_manager->SDL_textures`,
   `.c:69-72`) and then `DEALLOCATE_P(NULL)` reads `p->size_of__struct`
   (`.c:80`) → **NULL dereference**. (The guard at `.c:74` is dead:
   `index` is `u16`, so `index < 0` is never true — noted for the SDL module
   review.)
2. **Previously-released slot** → stale handle (aliased_texture **F1**: the
   fused `initialize_aliased_texture` never clears `texture`, by-value bug) →
   **double release** of the platform handle.

So under the SDL backend, calling `release_all_aliased_textures` on any
manager with fewer than 128 live textures (i.e. *any* real manager) crashes.

Why this is uncaught: the test
`aliased_texture_manager__release_all__resets_all_slots`
(`test_suite_rendering_aliased_texture_manager.c:53-68`) calls
`release_all_aliased_textures(0, &manager)` and passes — because the test
platform's `PLATFORM_release_texture` is a **no-op stub**
(`tests/core/source/PLATFORM.c:247-249`). Classic **Stub-real divergence**:
the suite validates the name-reset half of the release contract and silently
waives the platform half.

The targeted release functions (`by__alias`, `by__uuid`) are occupancy-safe by
construction (they locate via name/uuid, so only live slots are reached) — but
`by__uuid` on an F3-orphaned uuid silently fails to find, so the handle is
never released (another Leak-by-side-effect vector, closed by F3).

**Decision:**
- *pre v1.0.0:* make `release_all` occupancy-aware (skip
  `!is_aliased_texture__used` / `IS_DEALLOCATED_P` slots) — mirrors the
  targeted releases and removes the NULL-handle path.
- *post v1.0.0:* the double-release root cause is the record-level fused init
  (aliased_texture **F1**) and is closed by the init/dealloc discipline
  (`Life_Cycle_Patterns.design.md` §2).
- *cross-module:* the SDL NULL-guard gap is tracked for the
  `sdl_texture_manager` review, not acted on here.

### F6 — `p_OUT_` ownership contract contradicts the SSOT  ·  *pre v1.0.0 (doc)*

- `aliased_texture_manager.h:10-11`: *"WARNING: You do not own the returned
  texture."*
- `Life_Cycle_Patterns.md` §2 (the ownership **SSOT**): *"A parameter prefixed
  `p_OUT_` … is an out-parameter that the **caller owns**"* — and cites
  `allocate_texture_with__alias(..., Texture *p_OUT_texture)` **by name** as
  the worked example.

The two statements cannot both be the reference. The reconcilable reading: the
caller owns the **value** (the `Texture` struct storage it supplied); the
manager owns the **handle's life cycle** (exactly one
`PLATFORM_release_texture`, via the manager's release functions). Under that
reading the SSOT is correct and the header warning is the outlier — it
misstates the `p_OUT_` convention at the exact boundary where ownership is
most ambiguous. This is **Mode Confusion** on the ownership surface: one
surface form (`p_OUT_texture`) carrying two contradicting ownership readings.

Compounding it: `p_OUT_texture` is **silently optional** (`.c:71-73, 127-129`:
`NULL` is redirected to a stack `__tmp_texture`, whose populated value is then
discarded). The engine's convention for optional parameters is the
`OPTIONAL_` prefix (cf. `graphics_window_manager.c:110-111,113`); an optional
out-param named `p_OUT_` invites the caller to believe ownership transfers when
the value may simply vanish.

**Decision:** correct the header warning to state the SSOT reading (caller
owns the value; manager owns the handle), **pre v1.0.0** (doc-only). Renaming
to `OPTIONAL_p_OUT_texture` (or making the param mandatory) is a public-ABI
call — recorded, not acted.

### F7 — Path building in `load_texture_from__path_with__alias`  ·  *pre v1.0.0*

`.c:150-166`:

```c
Quantity__u32 length_of__base_directory = PLATFORM_get_base_directory(full_path);
if (MAX_LENGTH_OF__IO_PATH <= length_of__base_directory) { ... return true; }
full_path[length_of__base_directory++] = '/';
memcpy(&full_path[length_of__base_directory],
        c_str__path,
        MAX_LENGTH_OF__IO_PATH - length_of__base_directory);
```

- The `memcpy` copies a **fixed remainder** (`128 - len`) regardless of the
  source's actual length:
  - *short* `c_str__path` → reads **past the source's NUL** (out-of-bounds
    read of caller memory; the bytes past the NUL are copied but harmless to
    termination);
  - *long* `c_str__path` → truncated with **no NUL written** → an
    unterminated `IO_path` reaches `PLATFORM_allocate_texture_with__path`
    (downstream over-read).
- `c_str__path` is not NULL-checked (`memcpy(NULL, …)` is UB); only the *alias*
  name is validated.
- `PLATFORM_get_base_directory` failure is indistinguishable from an empty base
  directory (a `0` return yields `/relative/path`).

Contrast `set_c_str_of__aliased_texture`
(`aliased_texture.c:19-28`), which does it right (`strnlen`-bounded copy).

**Decision:** length-bounded copy with explicit terminator, NULL check on
`c_str__path`, **pre v1.0.0**.

### F8 — Duplicate aliases: unreachable second slot  ·  *pre v1.0.0*

`allocate_texture_with__alias` / `load_texture_from__path_with__alias` do not
check whether the name already exists. A second allocation under the same name
creates a second live slot; `get_p_aliased_texture_by__alias` (`.c:188-217`)
returns the **first match in index order**, so:

- the second slot is reachable **only by uuid** (and, via F3, not even that
  when created through `allocate_texture_with__alias`);
- `release_aliased_texture_by__alias` frees the *first* slot, orphaning the
  second → **Leak by side effect**.

The name→texture mapping is **Non-Injective** at two independent points:
duplicate names (here) and prefix-matching in
`is_c_str_matching__aliased_texture` (aliased_texture **F3**).

The header WARNING — *"repeated names will shadow textures in an unpredictable
manner"* — mischaracterises the behaviour: it is **Deterministic** (first
match wins); what is unmanaged is the *consequence* (the orphaned slot), which
the warning does not mention. **Surface-form leakage** in the contract.

**Decision:** policy decision **pre v1.0.0** — either reject duplicate names at
allocation (fail with the existing error convention) or document the
deterministic first-match semantic and require uuid-based release for the
shadowed slot. Reject-duplicate is the smaller contract.

### F9 — Unused `game.h` include (layer violation)  ·  *pre v1.0.0*

`aliased_texture_manager.c:4` includes `game.h` — the **Application** layer —
and uses nothing from it (no `Game` type appears in the file).

- 2.1: including a *higher*-layer header → **layer violation** (the
  Acyclic Dependencies direction is Rendering → below, never upward).
- 2.4: unused include.

The *call* direction is correct (Application `game.c` calling into this
module); only the stray include inverts the graph.

**Decision:** delete the include, **pre v1.0.0** (one line).

### F10 — Test suite gaps  ·  *pre v1.0.0*

`tests/core/source/rendering/test_suite_rendering_aliased_texture_manager.c`:

1. `..._get_uuid_of__aliased_texture__returns_unknown_when_not_found`
   (`.c:39-47`) — **vacuous**: body is `(void)uuid`; no assertion. It is the
   one test that would pin **F2**.
2. `..._release_all__resets_all_slots` (`.c:53-68`) — passes **only** against
   the no-op stub platform (see **F5**, Stub-real divergence).
3. **No coverage** of allocate/load, uuid round-trip, or failure rollback —
   the paths where **F3/F4** live.
4. All four tests cite `core/rendering/aliased_texture_manager.h.spec.md`
   — a **dangling spec reference**. Per `design_guide.md` §10.4 this is a
   known, in-progress condition of the spec reconstruction: **treated as a
   known gap, not a defect of this module.**

**Decision:** assert the sentinel in the uuid test; add a round-trip test
(allocate → `get_uuid_of__aliased_texture` → `get_texture_by__uuid` →
equivalence) and a failure-rollback test (stub platform returning failure;
assert slot returned to free state), **pre v1.0.0**.

---

## 5. Cross-Cutting Concerns (tracked, not acted on)

Per §11.3, these do not belong in this module's record alone; any new `./docs`
file they would require is **listed as a concern, not created**.

- **C1 — Address-seeded PRNGs.** Six managers
  (`aliased_texture_manager.c:33-36`, `graphics_window_manager.c:102-104`,
  `process_manager.c:63-65`, `entity_manager.c:56`, `game_action_manager.c:26`,
  `world.c:52`) seed `Repeatable_Psuedo_Random` with **the manager's own
  address**. Consequences: uuids are **ASLR-dependent** (not stable across
  runs), "repeatable" holds only within one address space, and any persisted
  uuid (saves, network) is non-portable between processes. This is an
  engine-wide convention, not a defect of this module — but it is a
  candidate for a new `./docs` topic (uuid/serialization conventions).
  **Concern: new `./docs` reference needed; not created at this time.**
- **C2 — The pipeline is Scaffolding.** Zero production callers for
  allocate/load/release; the registrar's `GEN` blocks are empty; the
  `Graphics_Window.*_tile_map__texture__uuid` setters have no callers, so the
  live lookup path is fed `IDENTIFIER__UNKNOWN__u32` and
  `gl_gfx_window.c:118-128,277-287` takes the failure branch (window
  disabled). F2/F3/F5 are therefore **latent** today but sit on the critical
  path once registration is generated/wired.
- **C3 — Caller-side error swallow (noted for SDL review).**
  `gl_render_world.c:293-299` ignores the `bool` return of
  `get_texture_by__uuid`; on failure the stack slot
  `array_of__sample_textures[i]` is **uninitialised** and a garbage texture
  would be bound. The module's error convention (true = failure) is
  consistent (9.1 ✓); this caller breaks 9.2 at its boundary. Tracked for the
  `gl_render_world` / SDL module pass.

---

## 6. Scores (per `design_pipeline.md`; 0 = clean, 5 = severe)

| § | Axis | Score | Anchor findings |
|:-:|------|:-----:|-----------------|
| 2 | Dependency direction | **2** | F9 (unused `game.h`, upward layer include) |
| 3 | Inversion of Control | **1** | clean parameter injection; no globals; C1 is cross-cutting |
| 4 | Information Hiding | **1** | header exposes only pool ops; 2-hop accessor chain (`game.h:203-206` ← `gfx_context.h:16-19`) is the engine idiom — Law of Demeter borderline, justified by layering (4.2.3) |
| 5 | Cohesion | **1** | one responsibility (the named-texture pool); dead fossil fn (F3) is minor |
| 6 | Ownership & Lifetime | **4** | F4 (no rollback), F5 (release policy), F6 (p_OUT_ dispute), F1 (stack) |
| 7 | Temporal Coupling & Contracts | **4** | F1 (double init, no idempotence), F3 (non-uniform postcondition), F8 (unmanaged duplicate semantics) |
| 8 | Concurrency | **1** | single-threaded engine-wide assumption, consistent with sibling managers; no module-specific state hazard |
| 9 | Error Boundary | **4** | F2 (NULL-deref fallthrough), F4 (partial state), C3 (caller swallow) |
| 10 | Stability & Change Impact | **2** | small API, few call sites; record struct lives in the `defines.h` monolith (field churn ripples broadly); interface partly pinned by tests (F10) |

- **Top 3 issues:** **F2** (crash on miss), **F3** (uuid Representation
  Invariant broken), **F5** (release path not viable under the real backend).
- **Blast radius estimate:** **Medium** — few call sites today, but the module
  is embedded in `Game` via `Gfx_Context`, its struct lives in the
  `defines.h` monolith, and the broken uuid invariant (F3) will affect every
  consumer the moment the Scaffolding pipeline (C2) is wired.
- **Refinement recommendation:** the single most impactful change is deleting
  the fossil re-init block in `allocate_texture_with__alias` (F3) — it
  restores the module's core contract (alias ↔ uuid ↔ handle round-trip) in
  one block deletion; pairing it with the `IDENTIFIER__UNKNOWN__u32` sentinel
  return (F2) and failure rollback (F4) makes the whole pool contract hold.

---

## 7. Timeline Summary

- **pre v1.0.0 (planned, not started):**
  - code: F2 (sentinel return) · F3 (delete re-init block + dead fn) · F4
    (failure rollback) · F5-policy (occupancy-aware `release_all`) · F7
    (path building) · F8 (duplicate-name policy) · F9 (drop `game.h` include) ·
    F1 (drop redundant init call in `game.c`)
  - doc: F6 (header warning vs SSOT)
  - tests: F10 (assert sentinel; round-trip + rollback tests)
- **post v1.0.0:** F1 (idempotence guard) · F5-root-cause (with aliased_texture
  F1, init/dealloc discipline) · F6 (optional-param naming, if adopted) · C1
  (address-seed convention, if a new `./docs` topic is opened)
- **Cross-module (tracked elsewhere):** C3 → `gl_render_world` / SDL pass ·
  SDL NULL-guard → `sdl_texture_manager` pass
- **Concerns for the documentation trees (per §11.3):** C1 implies a new
  `./docs` topic (uuid/serialization conventions) — **listed, not created**.
  No update to the existing `./docs` or `./agents/docs/design` references was
  deemed required at this time; the double-init instance (F1) could later be
  cited in `Life_Cycle_Patterns.design.md` §2 as a production occurrence.

> **No code has been changed.** This document records concerns and decisions
> for review. Tracking (`track_core_modules.py --track
> aliased_texture_manager`) is intentionally **not** run yet.
