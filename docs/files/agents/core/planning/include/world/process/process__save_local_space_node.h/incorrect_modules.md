# Planning: process__save_local_space_node — Incorrect Modules

**Review source:** `agents/core/review/include/world/process/process__save_local_space_node.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/process/process__save_local_space_node.h`
- `core/include/world/local_space.h`
- `core/include/serialization/serialization_request.h`
- `core/include/process/process.h`
- `core/source/world/*` (no implementing translation unit exists)

---

## 1. Problem Identification

**Flagged module:** `m_process__save_local_space_node(Process *p_this_process, Game *p_game)` — declared at `core/include/world/process/process__save_local_space_node.h:6-8`. Verdict: **Incorrect**.

Core defect: **Stub-real divergence / missing implementation.** The declaration is syntactically valid and matches the `m_Process` typedef (`void (*)(Process *, Game *)`), but no translation unit under `./core/source/` defines the symbol. Verified: `core/source/world/process/` is empty, and no world/process source file references `m_process__save_local_space_node`, `Serialization_Request`, or the handler dispatch pattern.

Secondary defect: **Under Specified Dispatch / dead declaration.** The function is never registered in any process table, never passed to `initialize_process` / `initialize_process_as__serialized_process`, and never called. It is an orphan declaration with no caller and no callee — the stated semantic intent (serialize a `Local_Space` node to a file via a filesystem process) has **no observable behavior** behind it. Any future attempt to take its address or dispatch it would be an undefined-reference linker error.

The declared Pre/Postconditions (write `Global_Space_Vector__3i32` + `Global_Space` metadata to the request's file handle, then `complete_process()`/`fail_process()`) are therefore **Contract-First** intent with no implementation to satisfy them — a **Translation Gap** between the documented contract and the (empty) real behavior.

## 2. Impact Assessment

Blast radius of the broken behavior is effectively **zero for existing code**, which is itself the finding:

- **No callers / no registration.** Nothing in `./include` or `./source` references the symbol, so no existing path depends on its (nonexistent) behavior. There is **no de facto contract** to invalidate — the de-facto contract today is "the function does not exist."
- **Sibling handlers share the same gap.** `process__load_chunk.h`, `process__save_chunk.h`, and `process__save_collision_node.h` are declared in the same directory, and `core/source/world/process/` is empty. If those siblings *also* lack implementations, the whole process-handler family is a batch of dead stub declarations — a **Coupled** cluster where the "broken behavior" (absence) is a shared condition. If they *do* have implementations elsewhere, then `save_local_space_node` is the single outlier in an otherwise working pattern.
- **What a correct implementation would couple to.** Realizing the intent would introduce new dependencies on:
  - `Serialization_Request` accessors (`is_serialization_request__writing`, `p_file_handler`) — the handler must read through `p_this_process->p_process_data` cast to `Serialization_Request *` (**Information Hiding** boundary; the handler must not bypass it).
  - `Local_Space` shape from `core/include/world/local_space.h`: its `Global_Space *` (`get_p_global_space_from__local_space`) and neighbor pointers. Serializing neighbor pointers requires a **Representation Invariant** decision (serialize by identity/key, not by raw pointer), otherwise the output is not **Round Trip Safe**.
  - File I/O (`PLATFORM_write_file`) and lifecycle (`complete_process`/`fail_process` from `process.h`).
- **Assumptions invalidated by the fix:** none in current code, because nothing assumes the behavior. The only assumption at risk is any *future* caller who would treat the declaration as an available API. Implementing it changes that assumption from "unresolvable" to "resolvable"; removing it makes the absence explicit rather than latent.

## 3. Resolution Assessment

Two mutually exclusive paths; pick one deliberately so the codebase does not retain an ambiguous stub.

**Path A — Implement (align to sibling pattern).**
1. Create `core/source/world/process/process__save_local_space_node.c` defining `m_process__save_local_space_node`.
2. Body: null-validate `p_this_process`, `p_this_process->p_process_data`, and `p_game` (**Precondition** guards; `Conservative` early-out to `fail_process`).
3. Cast `p_process_data` to `Serialization_Request *`; verify it is active and writing (`is_serialization_request__writing`, allocated).
4. Resolve the target `Local_Space` from the request's data pointer; guard with `is_local_space__allocated` / `is_local_space__active` (mirrors Precondition 4).
5. Serialize `Global_Space_Vector__3i32` + `Global_Space` metadata via `PLATFORM_write_file`; on I/O success call `complete_process()`, on any failure call `fail_process()` (**Postcondition**).
6. Register the handler where the other process handlers are dispatched (a process table / serializer) so it is no longer **Under Specified Dispatch**.

**Path B — Retire (remove the dead declaration).**
1. Delete `core/include/world/process/process__save_local_space_node.h` and any `#include` of it.
2. Confirm via a project-wide search that no file references the symbol (already verified: none). This converts a latent **Stub-real divergence** into an explicit absence, removing the risk of an accidental undefined-reference.

**Callers / docs:** No callers exist, so no caller updates are required under either path. If Path A is chosen, add the header to the build (new `.c` in `core/source/world/process/`) and document the serialization format (identity-based neighbor encoding) as the **Single Source of Truth** for `Local_Space` persistence.

**Blast radius:** Low. Behavior-preserving for all current callers (there are none). No de-facto contract is invalidated. A phased approach is **not** required for this function alone; however, if the sibling handlers (`save_chunk`, `load_chunk`, `save_collision_node`) are confirmed to be equally unimplemented, batch their resolution under one effort to keep the handler family **Orthogonal** and consistent rather than fixing only one stub.

## 4. Test Verification Checklist

- **Existing tests:** No test references `m_process__save_local_space_node` (`tests/core/source/world/test_suite_world_local_space.c` and process test suites contain no reference). Nothing asserts on the broken (absent) behavior, so **no existing assertion is invalidated**.
- **New tests (Path A):**
  - **Property Based Testing:** for any allocated `Local_Space`, serialization followed by deserialization preserves the `Global_Space_Vector__3i32` and `Global_Space` identity — verify the **Round Trip Property** / **Round Trip Check**.
  - **Equivalence Check:** serialized bytes are stable across repeated runs for identical input (determinism of the encoding).
  - **Fuzzing:** drive the handler with malformed/edge `Serialization_Request` states (null handle, inactive request, unallocated `Local_Space`, null `p_game`) to confirm every path terminates in `fail_process()` without UB — covers the **Boundary Condition** / null preconditions.
  - **Mutation Testing:** confirm the new tests catch a deliberately broken handler (e.g., missing `complete_process` call), validating suite quality.
- **Blast radius of tests:** Low–Medium (new tests only; no existing tests touched). No phased approach needed unless the sibling handlers are implemented in the same batch, in which case share a common serialization test harness to avoid **DRY** violations.

## 5. Blast Radius Summary

- **Files changed:** Path A → 1 new `.c` + build registration (+ tests); Path B → delete 1 `.h` (+ any including `#include`).
- **Behavior-preserving for current callers:** Yes — there are no callers; nothing relies on the broken behavior.
- **Phased approach needed:** No, for this function in isolation. Yes (batch) only if sibling process handlers are confirmed to share the same missing-implementation gap.
- **De-facto contracts invalidated:** None — the only "contract" today is nonexistence; the fix either realizes the documented intent or makes the absence explicit.
