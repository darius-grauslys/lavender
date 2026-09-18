# Outstanding Item 2 — Power-of-two process limit, two-pointer ring buffer, and `opaque_heap_sort`

**Question:** Rework `process_manager` around (a) a power-of-two `PROCESS_MAX_QUANTITY_OF` so
the pool can be a masked ring buffer (oldest/newest pointers), and (b) an
`opaque_heap_sort` over processes measured by (time running, priority). Does
`opaque_heap_sort` work on a ring buffer, or is something else better?

**Short answer: the power-of-two requirement is already met and is cheap; the two-pointer ring
is right for the *pool allocator*; but `opaque_heap_sort` should NOT be run on the ring itself —
it is a batch sort, and its invariants (root = extreme, parent/child index arithmetic) conflict
with the ring's FIFO invariants (oldest/newest delimiters). Split the design: ring buffer for
allocation, a separate flat "active list" for scheduling (batch-sorted per poll, or a live
indexed heap if you later want O(log n) ops). At n ≤ 16384 the per-frame batch sort is
CPU-negligible, so the simpler option wins.**

Date: 2026-09-17.

---

## 1. Current architecture (what the rework replaces)

`Process_Table` (`core/source/process/process_table.c`,
`core/include/process/process_priority_table_entry.c/.h`):

- One flat pointer array `Process *ptr_array_of__processes[PROCESS_MAX_QUANTITY_OF]`
  partitioned into `PROCESS_MAX_PRIORITY_LEVEL` (default 4) **contiguous bands**, each
  delimited by `p_ptr_process__oldest_of__priority` / `p_ptr_process__youngest_of__priority`.
- **Add** (`process_table.c:50-103`): walks higher bands, moves each non-empty one *up* one
  slot (`*++oldest = *youngest; *youngest = 0`, `priority_entry.c:28-44`) — O(number of higher
  bands), and inserts at the target band's tail. Empty bands are (re)initialized to sit after
  the lowest used lower band (lines 82-95).
- **Remove** (`process_table.c:105-133`): O(band size) scan from youngest→oldest, swap with
  the band's oldest, then move all lower bands down one slot each.
- **Poll** (`process_table.c:135-161` + `priority_entry.c:79-98`): round-robin one process per
  `poll_next` call, per-band cursor `p_ptr_process__current_priority_to__swap` wrapping within
  a band, bands visited in priority order, returns 0 after one full lap. `poll_process_manager`
  drains the whole table per frame (see Item 1, Mechanism C, for the budget bug layered on top).

Properties: O(1)-ish add, O(1) amortized poll, **O(n) remove in the worst band**, and the
band bookkeeping (sentinel-0 delimiters, "move up/down one" with array-end guards at
`priority_entry.c:33-36,52-55`) is the fragile part — a band pinned at the top of the array
makes `move_..._up` fail, which `add_process_to__process_table` treats as "full" even when
other regions have room.

## 2. The power-of-two requirement

- Core default `PROCESS_MAX_QUANTITY_OF = 512` (`BIT(9)`, `core/include/defines.h`);
  AncientsGame overrides to `BIT(14) = 16384` (`engine_config.h`, commit `9a982aa`).
  **Both are already powers of two** — the requirement is satisfied by the existing configs.
- Today the power of two buys nothing: pool allocation is **uuid open addressing**
  (`allocate_process_in__process_manager` → `get_next_available__allocation_in__contiguous_array`,
  `process_manager.c:119-137`; random or sequential uuids, linear probing on collision). The
  mask only matters once allocation switches to a **cursor ring**: `next = (cursor + 1) & MASK(n)`
  with `MASK(n) = n-1` — O(1) expected allocation, perfect cache locality, no probe chains, no
  "table full" ambiguity (empty slot is unambiguous: a zeroed `Serialization_Header` vs. an
  allocated one, as today).
- Recommendation: keep the power-of-two constraint (document it in `defines.h` next to the
  define), and add an `#if (PROCESS_MAX_QUANTITY_OF & (PROCESS_MAX_QUANTITY_OF-1)) #error`
  guard so a future config typo is a compile error, not a silent modulo bug.
- Consequence to manage: sequential cursor allocation changes **which slot** a uuid gets
  (today uuid = slot address via dehash). Nothing outside the pool should assume
  uuid ⇒ fixed slot; process uuids are runtime identifiers (used in tracing/debug), and
  processes are **not** persisted across save/load (verified in Item 3 — no process state is
  serialized), so there is no compatibility hazard.

## 3. Does `opaque_heap_sort` work on a ring buffer?

`heap_sort__opaque` (`core/source/sort/heap_sort__opaque.c`, header
`core/include/sort/heap_sort__opaque.h`): a **batch** in-place heapsort over a flat byte array,
with opaque `f_Sort_Heuristic__i32` (compare) and `f_Sort_Swap__Void` callbacks. Max-heap
variant (larger child wins when heuristic < 0); sort-down phase ends with the array sorted
descending by the heuristic.

Direct application to a two-pointer ring, and why it breaks:

1. **Geometry**: a heap needs `child = 2·root+1` index arithmetic. A *wrapped* circular buffer
   can be made to work with masked indices (`(2·root+1) & MASK`), but then "end of array"
   semantics (the `child >= length` break in the sort-down loop) no longer hold — you'd have to
   rewrite the sort for circular indexing. Not worth it; the ring's underlying array is
   already flat, so sort the flat array and forget the wrap.
2. **Invariants**: the ring's meaning *is* the oldest/newest delimiters (FIFO order, cursor
   for allocation). A full sort **destroys** that order every frame; the delimiters would
   become meaningless, and allocation-cursor bookkeeping would have to be rebuilt around
   sorted data — i.e. you'd have two competing ownership models in one array.
3. **Batch vs. live**: `heap_sort__opaque` re-sorts everything every call. Processes that
   *complete* mid-frame are removed (swap-with-tail), new ones added — a batch sort per poll
   absorbs both fine. But you cannot do O(log n) *insert* or O(log n) *delete-by-handle* with
   this API; if a process must be re-prioritized mid-frame (e.g. a waiter promoted when its
   neighbor finishes), you can't — you wait for the next frame's sort.

**Cost check (so "batch per frame" can be dismissed on merit, not instinct):** n = 16384 ⇒
~n·log₂n ≈ 230k comparisons + ≤ n swaps (of `Process*` pointers) per frame. At 32 frames/s
that's ~7M cheap comparisons/s — well under 1% of a core. The heap's asymptotic elegance buys
nothing at this scale; the batch sort is the pragmatic choice.

## 4. Recommended design (three separated concerns)

```
┌ pool (ownership) ─────────────────────────────────────────────┐
│ Process processes[2^k]  — two-pointer ring, cursor & mask     │
│ allocate: scan from cursor to first free slot (masked wrap)   │
│ free: mark header deallocated, advance cursor past it         │
└────────────────────────────────────────────────────────────────┘
┌ schedule (ordering) ──────────────────────────────────────────┐
│ Process *active[2^k] — flat list, append on add,              │
│ swap-with-tail remove on finish                                │
│ each poll_process_manager:                                     │
│   heap_sort__opaque(active, count, sizeof(Process*),          │
│       cmp = (priority asc, then start-tick asc))               │
│   walk from head: run each handler until the frame-time        │
│   budget (u32F20, Item 1 §8.1) is spent; criticals always run  │
└────────────────────────────────────────────────────────────────┘
┌ timeout (liveness) ───────────────────────────────────────────┐
│ per-process tick timer with correct units (Item 1 §8.3);      │
│ timed-out process => fail + release, slot returned to ring    │
└────────────────────────────────────────────────────────────────┘
```

- **Key for the sort**: `(process_priority__u8, process start tick)`. Start tick = the game
  tick at allocation (`initialize_process`), which is exactly "time the process has been
  running" (monotonic ⇒ unique ⇒ stable ordering; no tie-breaker sequence needed unless two
  processes allocate in the same tick — add a monotonically-increasing allocation counter as
  the final tie-break if that matters).
- **Budget**: poll from the sorted head; stop when the accumulated u32F20 exceeds the tick
  quantum (`BIT(20)`) — except `is_process__critical` entries, which always run (preserves the
  existing critical semantics and the store/resolve/TCP behavior).
- **Why a separate `active` array instead of sorting the ring in place**: the ring serves
  allocation (needs stable slots + cursor); the active list serves scheduling (needs total
  order). One array, two ownership models = the exact conflict in §3. Two arrays = each
  invariant is local. Memory: one extra `2^k` pointer array (64 KB at 16384) — trivial.
- **What this fixes vs. today**: O(n) worst-case remove → O(1) swap-with-tail; band
  bookkeeping deleted entirely (no sentinel-0 delimiters, no move-up/down, no "full" false
  positives); the schedule is deterministic and budget-bounded (Item 1, Mechanism C gone by
  construction); polling order is oldest-first within priority (fair), instead of the
  current insert-rotation quirk of the band scheme.

## 5. Alternative considered: live indexed d-ary heap

An indexed (handle-based) binary/d-ary heap gives O(log n) push/pop/delete-by-handle and
survives mid-frame priority changes without a re-sort. It would require a **new** opaque sort
API (the current one has no index map and no keyed delete) or a hand-rolled heap in
`process_manager`. Given §3's cost check, **do not build this now** — revisit only if a
profiler ever shows the per-frame sort or the O(n) walks matter (at 2^14 entries, they won't;
the chunk generators' dehash polling will dominate, see Item 1).

## 6. Migration risks

- `p_enqueued_process` / `enqueue_process` / `set_process_as__dequeued`
  (`process_manager.c:170-182`) form a separate waiting mechanism keyed on process pointers —
  reordering the schedule array does not affect it, but the rework must keep the
  dequeue-on-finish semantics intact (a completed process dequeues its waiter).
- `p_process__latest` (`process_manager.c:157,227-228`) is set but has no readers found in
  core — candidate for deletion in the rework (verify against game-side uses first).
- Games may register priorities beyond the 4-band default
  (`PROCESS_MAX_PRIORITY_LEVEL`, `defines.h`); the new design's sort key handles any priority
  count with no table changes.
- The `debug_info` line at `process_manager.c:162` (per-frame process count) — move it behind
  a debug flag while reworking; it doubles as the migration canary (occupancy trend).

## 7. Decision summary

| Option | Verdict |
|---|---|
| Power-of-two `PROCESS_MAX_QUANTITY_OF` | **Adopt** (already true; add compile-time guard) |
| Two-pointer ring as the *pool allocator* | **Adopt** (masked cursor, O(1) alloc, no probe chains) |
| `opaque_heap_sort` run **on the ring** | **Reject** (invariant conflict; circular geometry breaks the batch sort) |
| `opaque_heap_sort` over a **separate active list**, per poll | **Adopt** (~230k comparisons/frame at max size — negligible) |
| Live indexed heap | Defer (only if profiling justifies) |
| Frame-time budget in the poll loop | **Adopt** (required; see Item 1 §8.1) |
