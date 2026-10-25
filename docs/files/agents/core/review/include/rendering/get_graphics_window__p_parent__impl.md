get_graphics_window__p_parent — core/source/rendering/graphics_window_manager.c

Resolves and returns the parent Graphics_Window of a given child window by looking up the child's stored parent UUID across the manager's contiguous window pool. Returns null when the child has no parent (invalid parent UUID) or when no pool window matches the stored parent UUID.

Pre-conditions:
1. p_graphics_window_manager must be a non-null pointer to an initialized Graphics_Window_Manager. This function only reads p_graphics_window_manager->graphics_windows (the contiguous pool); it does not use ptr_array_of__sorted_graphic_windows.
2. p_graphics_window must be a non-null pointer to a Graphics_Window whose graphics_window__parent__uuid field is valid (the function dereferences p_graphics_window immediately, with no null guard).
3. No null validation is performed by this function; ensuring non-null arguments is the caller's responsibility.
4. The manager's graphics_windows array must have been initialized (e.g. via initialize_graphics_window_manager), which sets unallocated slots' uuids to IDENTIFIER__UNKNOWN__u32.

Post-conditions:
1. On success, returns a pointer to the Graphics_Window in p_graphics_window_manager->graphics_windows whose uuid equals p_graphics_window->graphics_window__parent__uuid. The returned pointer aliases the manager's contiguous pool.
2. Returns null (0) when p_graphics_window->graphics_window__parent__uuid is IDENTIFIER__UNKNOWN__u32 (the child has no parent).
3. Returns null (0) when no window in the pool has a uuid matching the child's parent uuid (e.g. the parent was released and its slot reset to UNKNOWN — a dangling parent reference).
4. The function is read-only: no manager or window state is mutated by it.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent. The early check on is_identifier_u32__invalid correctly short-circuits the "child has no parent" case. The linear scan compares the child's stored graphics_window__parent__uuid against each candidate's uuid (obtained via GET_UUID_P) and returns the match. This is an exact UUID-based parent resolution, matching the function's purpose as the parent-lookup primitive used by get_graphics_window__p_root_parent.

Implementation Correctness:
Type compatibility — is_identifier_u32__invalid takes Identifier__u32 (uint32_t) and graphics_window__parent__uuid is Identifier__u32 (Graphics_Window, graphics_window_manager.c:2495 of defines.h); exact match, no implicit conversion. GET_UUID_P returns Identifier__u32 (uint32_t), so the equality comparison with graphics_window__parent__uuid is uint32_t == uint32_t with no truncation. Index__u32 (uint32_t) is compared against the int literal MAX_QUANTITY_OF__GRAPHICS_WINDOWS (8); the int is promoted to uint32_t, which is safe and in-range.
Undefined behavior — no null dereference of p_graphics_window__parent_candidate: get_p_graphics_window_by__index_from__manager returns &p_graphics_window_manager->graphics_windows[index], which is always a valid, non-null pointer for in-range indices. The loop bounds (0 .. MAX_QUANTITY_OF__GRAPHICS_WINDOWS-1) guarantee the index is always in range, so the helper's internal out-of-range guard never fires and GET_UUID_P is never applied to null. Reading unallocated slots is safe: initialize_graphics_window_manager zeroes them to IDENTIFIER__UNKNOWN__u32, which cannot equal a valid parent uuid, so no false-positive match occurs. The GET_UUID_P cast (Graphics_Window* -> Serialization_Header* -> .uuid) reads the header uuid field that is the first member of Graphics_Window (defines.h:2483), so it reads a genuine field at offset 0 rather than type-punning; this is the established codebase pattern (cf. get_p_parent_of__graphics_window in graphics_window.h:399).
Validation — no null checks are performed on either parameter. This is appropriate here: the sole caller, get_graphics_window__p_root_parent (graphics_window_manager.c:689), guarantees a non-null manager and a non-null parent candidate. However, since this is a public (non-static) function declared in graphics_window_manager.h, the absence of an NDEBUG guard is a minor consistency gap versus sibling helpers such as get_p_parent_of__graphics_window (graphics_window.h:393), which does guard p_graphics_window. It is a robustness gap, not a correctness defect.

Side Effects:
No side effects. The function is a pure read-only lookup over the manager's contiguous window pool; it mutates no state, performs no allocation, issues no I/O, and changes nothing that outlives the call.
