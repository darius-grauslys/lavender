# allocate_serialization_header

**File of origin:** `core/include/serialization/hashing.h`

## Semantic

Allocates a serialization header from a contiguous array by randomly selecting an available slot. The function delegates to `get_next_available__random_allocation_in__contiguous_array` to find a free slot and obtain a UUID, then initializes the header in-place via the `ALLOCATE_P` macro. Returns a pointer to the allocated header, or NULL if no slot is available.

## Pre-conditions

1. `p_serialization_headers` must point to a valid contiguous array of `Serialization_Header` structs, or be NULL (in which case the underlying lookup will return NULL).
2. `length_of__p_serialization_headers` specifies the number of elements in the array; must match the actual allocation.
3. `p_randomizer` must be a valid, initialized `Repeatable_Psuedo_Random` instance.

## Post-conditions

1. If a free slot was found, the returned pointer points to a `Serialization_Header` whose `uuid` and `size_of__struct` fields have been initialized (via `initialize_serialization_header`).
2. If no free slot was found, the function returns NULL.
3. The `uuid__u32` local variable is updated with the resolved UUID (valid only if a slot was found).

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's intent is to find an available slot, initialize its header with a UUID, and return a pointer to it. The implementation correctly delegates to `get_next_available__random_allocation_in__contiguous_array` for slot discovery. However, the `ALLOCATE_P` macro is invoked **unconditionally** — without checking whether `p_serialization_header` is NULL.

The underlying function `get_next_available__allocation_in__contiguous_array` (called transitively) explicitly returns `0` (NULL) when no available slot is found (`index_of__allocation == INDEX__UNKNOWN__u32`). This means `p_serialization_header` can legitimately be NULL upon return.

When NULL is passed to `ALLOCATE_P`, the macro expands to:

```c
initialize_serialization_header(
    (Serialization_Header*)p_serialization_header,
    uuid,
    ((Serialization_Header*)p_serialization_header)->size_of__struct)
```

The third argument dereferences `p_serialization_header` to read `size_of__struct` **before** `initialize_serialization_header` is even called. This is a NULL pointer dereference, causing undefined behavior (typically a crash).

The correct pattern is already established in the sibling function `allocate_serialization_header_with__this_uuid` (same file, lines 108–120), which guards the call with `if (p_serialization_header)`. The `allocate_serialization_header` function should follow the same pattern.

## Implementation Correctness

- **Type compatibility:** All parameter types match their intended targets. No implicit conversions or truncation.
- **Undefined behavior:** NULL pointer dereference occurs in the `ALLOCATE_P` macro when `get_next_available__random_allocation_in__contiguous_array` returns NULL. The macro dereferences the pointer to read `size_of__struct` before passing it to `initialize_serialization_header`, which also dereferences the pointer.
- **Validation:** The function lacks a NULL check on `p_serialization_header` before calling `ALLOCATE_P`. This validation is the function's own responsibility — it should not blindly pass a potentially-NULL pointer into a macro that dereferences it. The sibling function `allocate_serialization_header_with__this_uuid` demonstrates the correct approach.

## Side Effects

- **Mutates:** The `Serialization_Header` struct at the allocated slot (sets `uuid` and `size_of__struct` fields via `initialize_serialization_header`), and updates the `uuid__u32` output parameter of the underlying lookup function.
- **No side effects** if no slot is available (the function should simply return NULL without touching memory — but currently it does dereference NULL, which is the bug).

## Fix

Add a NULL guard before invoking `ALLOCATE_P`, matching the pattern in `allocate_serialization_header_with__this_uuid`:

```c
if (p_serialization_header)
    ALLOCATE_P(p_serialization_header, uuid__u32);
```

## Additional Notes

The same missing-NULL-check bug pattern also appears in the sibling functions `allocate_serialization_header_with__uuid_branding` (line 150), `allocate_serialization_header__u64` (line 230), and `allocate_serialization_header_with__uuid_branding__u64` (line 247). These should be reviewed and fixed similarly.
