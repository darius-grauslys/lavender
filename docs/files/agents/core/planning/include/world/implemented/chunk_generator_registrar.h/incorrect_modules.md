# Planning: chunk_generator_registrar.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/implemented/chunk_generator_registrar.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/implemented/chunk_generator_registrar.h`
- `core/source/world/implemented/chunk_generator_registrar.c`
- `core/include/world/chunk_generator_table.h`
- `core/source/world/chunk_generator_table.c`
- `core/include/types/implemented/world/chunk_generator_kind.h`
- `core/include/defines_weak.h`
- `examples/template-files/source/world/implemented/chunk_generator_registrar.c`
- `examples/template-files/include/world/implemented/chunk_generator__overworld.h`
- `examples/template-files/source/world/implemented/chunk_generator__overworld.c`
- `tests/core/source/world/implemented/test_suite_world_implemented_chunk_generator_registrar.c`
- `tests/core/include/world/implemented/test_suite_world_implemented_chunk_generator_registrar.h`

---

## 1. Problem Identification

### `register_chunk_generators` — `Stub-real divergence`

The function `register_chunk_generators` in
`core/source/world/implemented/chunk_generator_registrar.c` is a **stub** that
diverges from its real semantic intent. It emits only
`debug_warning("register_chunk_generators, impl.")` and performs no calls to
`register_chunk_generator_into__chunk_generator_table`. This is a
**Translation Gap** between the function's documented post-condition (all
`Chunk_Generator_Kind` entries between GEN-BEGIN and GEN-END are registered)
and the actual no-op behavior.

The `Chunk_Generator_Kind` enum in
`core/include/types/implemented/world/chunk_generator_kind.h` currently has no
concrete kinds defined between its GEN-BEGIN and GEN-END markers — only
`Chunk_Generator_Kind__None` and `Chunk_Generator_Kind__Unknown`. The
template at `examples/template-files/source/world/implemented/chunk_generator_registrar.c`
shows the expected pattern: include the concrete generator header and call
`register_chunk_generator_into__chunk_generator_table` for each kind. The actual
implementation omits both the includes and the registration calls.

## 2. Impact Assessment

### Caller coupling

`initialize_chunk_generator_table` in `core/source/world/chunk_generator_table.c`
is **Coupled** to `register_chunk_generators` — it calls it as the final step
of table initialization (line 64). Because `register_chunk_generators` is a
no-op, only `Chunk_Generator_Kind__None` (the default generator) is ever
populated in the `M_process__chunk_generators` array. All other slots remain
NULL (zero-initialized by `memset`).

### Downstream lookup risk

Any code calling `get_chunk_generator_process_from__chunk_generator_table`
with a non-None kind receives a NULL `m_Process` pointer. If the caller
does not null-check before invocation, this results in undefined behavior
(null function pointer call). Currently no concrete kinds exist in the enum,
so no code path exercises this yet — but the **Boundary Condition** of the
enum (kinds between GEN-BEGIN and GEN-END) is not enforced by registration.

### `get_default_chunk_generator_process` (inline helper)

The inline helper in `core/include/world/chunk_generator_table.h` uses only
`Chunk_Generator_Kind__None`, which is correctly registered by
`initialize_chunk_generator_table` directly. This path is **not** affected by
the stub.

### Test coverage gap

The test suite in
`tests/core/source/world/implemented/test_suite_world_implemented_chunk_generator_registrar.c`
only verifies a non-crash smoke test (`chunk_generator_registrar__register_does_not_crash`).
It does not assert that any generators are actually registered. This test
asserts **broken behavior** by omission — it passes regardless of whether
registration occurs.

### De facto contract

There is no de facto contract relying on the no-op behavior. The
`initialize_chunk_generator_table` review explicitly notes the stub is
"intended to register additional generators" but is currently a no-op.
Correcting this does not invalidate any existing assumption — all current
callers only depend on `Chunk_Generator_Kind__None`.

## 3. Resolution Assessment

### Step 1 — Implement `register_chunk_generators`

Replace the `debug_warning` stub in
`core/source/world/implemented/chunk_generator_registrar.c` with actual
registration calls following the template pattern. The function must:

- Include `types/implemented/chunk_generator_kind.h` (for the enum values).
- Include `world/chunk_generator_table.h` (for
  `register_chunk_generator_into__chunk_generator_table`).
- Include each concrete generator header (e.g.,
  `world/implemented/chunk_generator__overworld.h`) between GEN-INCLUDE-BEGIN
  and GEN-INCLUDE-END markers.
- Call `register_chunk_generator_into__chunk_generator_table` for each
  concrete `Chunk_Generator_Kind` value between GEN-BEGIN and GEN-END markers.

The structure should mirror the template:

```c
#include "world/implemented/chunk_generator_registrar.h"
#include "types/implemented/chunk_generator_kind.h"
#include "world/chunk_generator_table.h"

// GEN-INCLUDE-BEGIN
#include "world/implemented/chunk_generator__overworld.h"
// GEN-INCLUDE-END

void register_chunk_generators(
        Chunk_Generator_Table *p_chunk_generator_table) {
    // GEN-BEGIN
    register_chunk_generator_into__chunk_generator_table(
            p_chunk_generator_table,
            Chunk_Generator_Kind__Overworld,
            m_process__chunk_generator__overworld);
    // GEN-END
}
```

### Step 2 — Add concrete kinds to the `Chunk_Generator_Kind` enum

Add concrete enum values (e.g., `Chunk_Generator_Kind__Overworld`) between
the GEN-BEGIN and GEN-END markers in
`core/include/types/implemented/world/chunk_generator_kind.h`. This ensures
the enum serves as the **Single Source of Truth (SSOT)** for all valid
generator kinds, and the registration calls in Step 1 reference valid enum
values.

### Step 3 — Create concrete generator implementations

Create concrete chunk generator implementations in the core tree:
- `core/include/world/implemented/chunk_generator__overworld.h`
- `core/source/world/implemented/chunk_generator__overworld.c`

These should follow the template at
`examples/template-files/source/world/implemented/chunk_generator__overworld.c`.

### Step 4 — Update tests

Update `test_suite_world_implemented_chunk_generator_registrar.c` to verify
that concrete generators are registered after calling `register_chunk_generators`.
Use a **Round Trip Check**: register a kind, then retrieve it via
`get_chunk_generator_process_from__chunk_generator_table` and assert the
returned `m_Process` is non-NULL and matches the expected function pointer.
Add **Property Based Testing** assertions that for each kind in the enum
(between GEN-BEGIN and GEN-END), the table entry is non-NULL after
initialization.

### Phased approach

Not required. The changes are **additive** — adding new registrations does not
change behavior for `Chunk_Generator_Kind__None`, which remains the default.
No existing caller relies on the no-op behavior.

## 4. Test Verification Checklist

### Existing tests

- `test_suite_world_implemented_chunk_generator_registrar.c` contains only
  `chunk_generator_registrar__register_does_not_crash`, a non-crash smoke test.
  It does **not** assert correct registration. The fix will not invalidate
  this test (it will still pass), but it is insufficient.

### New tests needed

- **Round Trip Check**: After `initialize_chunk_generator_table`, retrieve
  each registered kind via `get_chunk_generator_process_from__chunk_generator_table`
  and assert the returned `m_Process` matches the expected function pointer.
- **Property Based Testing**: For each `Chunk_Generator_Kind` value between
  GEN-BEGIN and GEN-END, assert the table entry is non-NULL after
  initialization.
- **Equivalence Check**: Verify that `get_default_chunk_generator_process`
  still returns `_m_chunk_generator__default` after the change (behavior
  preservation for the default path).

### Blast radius: **Low**

- Only `core/source/world/implemented/chunk_generator_registrar.c` changes
  behavior.
- No existing caller depends on the no-op behavior.
- The `Chunk_Generator_Kind` enum currently has no concrete kinds, so the
  registration calls will be empty until concrete kinds are added (Step 2).
- A **Fuzzing** boundary test for `get_chunk_generator_process_from__chunk_generator_table`
  with out-of-range enum values is recommended but already covered by the
  debug-mode bounds check in `chunk_generator_table.c`.

## 5. Blast Radius Summary

- **Files needing changes**: 1 (the registrar `.c`), plus the enum header,
  new concrete generator files, and test files — **4 files total**.
- **Behavior-preserving for current callers**: Yes — all current callers only
  use `Chunk_Generator_Kind__None`, which is registered directly by
  `initialize_chunk_generator_table` and is unaffected.
- **Phased approach needed**: No. Changes are additive.
- **De facto contracts invalidated**: None. The no-op behavior was never
  relied upon as a contract.
