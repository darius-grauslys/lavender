get_catagory_size_of__p_ui_tile_map__wrapper — core/include/ui/ui_tile_map.h

**File of origin:** `core/include/ui/ui_tile_map.h`

---

## Semantic

Returns the size category (`UI_Tile_Map_Size` enum value) stored in the `catagory_size_of__ui_tile_map` field of a `UI_Tile_Map__Wrapper` struct.

---

## Pre-conditions

1. `p_ui_tile_map__wrapper` must be a non-null pointer to a valid `UI_Tile_Map__Wrapper` struct. Passing `NULL` results in undefined behavior (null pointer dereference). This is consistent with the codebase convention for all `get_*_of__p_ui_tile_map__wrapper` inline accessors, which assume the caller provides a valid pointer.

---

## Post-conditions

1. Returns the value of the `catagory_size_of__ui_tile_map` field (type `UI_Tile_Map_Size`) from the pointed-to `UI_Tile_Map__Wrapper` struct.
2. The struct is not mutated; the function is a pure read accessor.

---

## Correctness Verdict

**Correct**

---

## Semantic Alignment

The function correctly accesses and returns the `catagory_size_of__ui_tile_map` field of the `UI_Tile_Map__Wrapper` struct. The field is defined as `UI_Tile_Map_Size catagory_size_of__ui_tile_map;` in the struct definition (see `core/include/defines.h`, line 1542). The return type `UI_Tile_Map_Size` matches the field type exactly. The semantic intent — providing read access to the size category — is fulfilled.

---

## Implementation Correctness

- **Type compatibility:** The return type `UI_Tile_Map_Size` matches the field type `UI_Tile_Map_Size` exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** No undefined behavior is present, assuming the pre-condition (non-null pointer) is met. There is no broken pointer arithmetic, no type punning, and no out-of-bounds access. The function dereferences the pointer and accesses a single struct field via the `->` operator, which is well-defined for a valid pointer.
- **Validation appropriateness:** No null-check or validation is performed within the function. This is appropriate for its role as a lightweight `static inline` accessor — the established convention in this module is that callers are responsible for ensuring the pointer is valid. The function's own responsibility is to read and return the field, which it does correctly.

---

## Side Effects

No side effects. This is a pure read accessor: it dereferences the pointer, reads the `catagory_size_of__ui_tile_map` field, and returns its value. It does not modify the struct or any other observable state.
