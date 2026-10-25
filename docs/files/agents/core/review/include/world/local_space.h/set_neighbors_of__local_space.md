# set_neighbors_of__local_space

**File of origin:** `core/include/world/local_space.h`

## Semantic

Sets the six directional neighbor pointers (north, east, south, west, above, below) on a `Local_Space` struct, establishing adjacency links to neighboring local spaces.

## Pre-conditions

1. `p_local_space` must be a non-null pointer to a writable `Local_Space` object.
2. Each of the six neighbor parameters (`p_local_space__north`, `p_local_space__east`, `p_local_space__south`, `p_local_space__west`, `p_local_space__above`, `p_local_space__below`) may be NULL (representing no neighbor in that direction) or a valid pointer to a `Local_Space` object.
3. The `Local_Space` struct pointed to by `p_local_space` must be in a valid state to receive pointer assignments (i.e., not corrupted).

## Post-conditions

1. The `p_local_space` struct is mutated so that its six neighbor pointer fields (`p_local_space__north`, `p_local_space__east`, `p_local_space__south`, `p_local_space__west`, `p_local_space__above`, `p_local_space__below`) now hold the values of the corresponding parameters passed to the function.
2. No other fields of the `Local_Space` struct are modified.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly assigns all six neighbor pointer parameters to their corresponding struct fields in the `Local_Space` struct. The struct definition (in `core/include/defines.h`) contains exactly these six neighbor pointer fields, and the function writes to all six — no member is omitted, and no reordering occurs. The parameter-to-field mapping is direct and one-to-one:

- `p_local_space__north` → `p_local_space->p_local_space__north`
- `p_local_space__east` → `p_local_space->p_local_space__east`
- `p_local_space__south` → `p_local_space->p_local_space__south`
- `p_local_space__west` → `p_local_space->p_local_space__west`
- `p_local_space__above` → `p_local_space->p_local_space__above`
- `p_local_space__below` → `p_local_space->p_local_space__below`

## Implementation Correctness

- **Type compatibility:** All parameter types (`Local_Space *`) match the target field types (`struct Local_Space_t *`). Since `Local_Space` is a typedef for `struct Local_Space_t` (declared in `defines_weak.h` and defined in `defines.h`), these types are identical. No implicit conversions or truncation occur.
- **Undefined behavior:** No pointer arithmetic, no null dereference (the function dereferences `p_local_space` which must be non-null per pre-conditions), no type punning, no out-of-bounds access.
- **Validation:** No validation is needed within this function — it is a low-level inline struct assignment helper. Ensuring `p_local_space` is non-null is the caller's responsibility.

## Side Effects

The function mutates the `Local_Space` struct pointed to by `p_local_space` by writing to its six neighbor pointer fields. No other side effects — no I/O, no memory allocation, no global state changes.
