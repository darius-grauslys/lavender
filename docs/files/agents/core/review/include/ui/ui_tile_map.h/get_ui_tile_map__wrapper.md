# get_ui_tile_map__wrapper

**File of origin:** `core/include/ui/ui_tile_map.h`, lines 126-138

---

## Semantic

Constructs and returns a `UI_Tile_Map__Wrapper` struct by packaging the provided tile data pointer, tile map dimensions, and size category into a single value-type wrapper. This is a pure construction function — it does not allocate resources, mutate any external state, or perform RAII. It is a convenience factory for the `UI_Tile_Map__Wrapper` struct.

---

## Pre-conditions

1. `p_ui_tile_data` — may be null or non-null; no constraint enforced by this function. The caller is responsible for providing valid data if a valid wrapper is expected.
2. `p_ui_tile_map__flags` — **unused parameter** (see Side Effects / Implementation Correctness). No constraint required; the value is never read or dereferenced.
3. `width_of__tile_map` — must be a valid `Quantity__u32` value. No range validation is performed by this function.
4. `height_of__tile_map` — must be a valid `Quantity__u32` value. No range validation is performed by this function.
5. `catagory_size_of__ui_tile_map` — must be a valid `UI_Tile_Map_Size` enum value. No range validation is performed by this function.

---

## Post-conditions

1. Returns a `UI_Tile_Map__Wrapper` struct with all four fields populated in declaration order:
   - `p_ui_tile_data` ← `p_ui_tile_data`
   - `width_of__ui_tile_map` ← `width_of__tile_map`
   - `height_of__ui_tile_map` ← `height_of__tile_map`
   - `catagory_size_of__ui_tile_map` ← `catagory_size_of__ui_tile_map`
2. No external state is modified. The returned struct is a value copy.

---

## Correctness Verdict

**Correct**

---

## Semantic Alignment

The implementation fulfills its semantic intent: it constructs a `UI_Tile_Map__Wrapper` from the provided parameters. The struct initializer uses positional initialization in the exact declaration order of the struct fields (verified against the struct definition in `core/include/defines.h`, lines 1538-1543):

```c
typedef struct UI_Tile_Map__Wrapper_t {
    UI_Tile_Raw *p_ui_tile_data;
    Quantity__u32 width_of__ui_tile_map;
    Quantity__u32 height_of__ui_tile_map;
    UI_Tile_Map_Size catagory_size_of__ui_tile_map;
} UI_Tile_Map__Wrapper;
```

The initializer in `get_ui_tile_map__wrapper` assigns:
1. `p_ui_tile_data` → `p_ui_tile_data` (field 1) ✓
2. `width_of__tile_map` → `width_of__ui_tile_map` (field 2) ✓
3. `height_of__tile_map` → `height_of__ui_tile_map` (field 3) ✓
4. `catagory_size_of__ui_tile_map` → `catagory_size_of__ui_tile_map` (field 4) ✓

All struct fields are assigned, no member is omitted, and no reordering occurs.

---

## Implementation Correctness

- **Type compatibility:** All parameter types match their corresponding struct field types exactly:
  - `UI_Tile_Raw *` → `UI_Tile_Raw *` ✓
  - `Quantity__u32` → `Quantity__u32` ✓
  - `Quantity__u32` → `Quantity__u32` ✓
  - `UI_Tile_Map_Size` → `UI_Tile_Map_Size` ✓
  No implicit conversions or truncation occur.

- **Undefined behavior:** No undefined behavior. No pointer dereferencing, no pointer arithmetic, no out-of-bounds access. The function simply returns a value-initialized struct.

- **Validation:** No validation is performed, which is appropriate for this function's role as a lightweight struct constructor. Validation of the wrapper's validity is delegated to separate predicate functions (`is_ui_tile_map__wrapper__valid`, etc.).

- **Unused parameter:** The parameter `UI_Tile_Map__Flags *p_ui_tile_map__flags` is accepted but never used in the function body. The `UI_Tile_Map__Wrapper` struct has no flags field, and the parameter is not stored or read. This is a code smell (dead parameter) but does not cause incorrect behavior. The callers (`ui_tile_map__small_to__ui_tile_map_wrapper`, etc.) pass `&p_ui_tile_map__small->ui_tile_map__flags` etc., which is harmless since the value is never dereferenced.

---

## Side Effects

No side effects. The function is a pure value constructor: it reads its input parameters and returns a new `UI_Tile_Map__Wrapper` by value. No memory is modified, no I/O occurs, and no callee functions are invoked.

---

## Lavender-Specific Semantics

This function is **not** an initialization function in the Lavender sense. It is named `get_ui_tile_map__wrapper`, not `initialize_*` or `reset_*`. It does not clean up a struct to initial conditions, nor does it remove elements from pools. It is a factory function that constructs a new wrapper struct from provided components. Therefore, the Lavender "Initialization ≠ RAII" distinction does not apply here.
