get_width_of__p_ui_tile_map__wrapper — core/include/ui/ui_tile_map.h

Returns the width field of a UI_Tile_Map__Wrapper struct.

Pre-conditions:
1. p_ui_tile_map__wraper must be a non-null pointer to a valid UI_Tile_Map__Wrapper struct.

Post-conditions:
1. Returns the value of width_of__ui_tile_map (a Quantity__u32) from the pointed-to UI_Tile_Map__Wrapper struct.
2. The struct is not mutated.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly accesses and returns the width_of__ui_tile_map field of the UI_Tile_Map__Wrapper struct. The return type Quantity__u32 matches the field type exactly. The field is part of the struct definition (see defines.h line 1540). The semantic intent — providing read access to the width — is fulfilled.

Implementation Correctness:
Type compatibility — the return type Quantity__u32 matches the field type Quantity__u32 exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (pre-condition requires non-null), no type punning, no out-of-bounds access.
No validation is needed — this is a simple accessor. The caller is responsible for ensuring p_ui_tile_map__wraper is valid.

Side Effects:
No side effects — the function is a pure read accessor. It does not modify any state.
