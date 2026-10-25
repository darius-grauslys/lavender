_allocate_graphics_window_from__graphics_window_manager — core/source/rendering/graphics_window_manager.c (lines 107-191)

Allocates a Graphics_Window from the manager's contiguous pool (optionally using a caller-provided UUID and platform window), populates its fields, registers it in the sorted pointer array, and re-sorts. Returns a pointer to the allocated window, or 0 on failure.

Pre-conditions:
1. p_gfx_context must be non-null (used only when OPTIONAL_p_PLATFORM_graphics_window is null, to call PLATFORM_allocate_gfx_window).
2. p_graphics_window_manager must be non-null and properly initialized: its graphics_windows array has serialization headers set to IDENTIFIER__UNKNOWN__u32 with size_of__struct = sizeof(Graphics_Window), its ptr_array_of__sorted_graphic_windows is zero-initialized (all NULL), and its randomizer is seeded.
3. OPTIONAL_p_PLATFORM_graphics_window may be null (triggers PLATFORM_allocate_gfx_window) or a valid pointer to an existing PLATFORM_Graphics_Window.
4. OPTIONAL_uuid__u32 may be IDENTIFIER__UNKNOWN__u32 (triggers random UUID generation via the manager's randomizer) or a specific UUID. The caller is responsible for ensuring a specific UUID does not collide with an already-allocated slot.
5. texture_flags_for__gfx_window must encode valid width/height texture dimensions (bits 0-2 = height enum, bits 3-5 = width enum, per TEXTURE_FLAG__LENGTH__BIT_COUNT = 3).
6. The manager must have at least one free slot in graphics_windows and one NULL entry in ptr_array_of__sorted_graphic_windows for allocation to succeed.

Post-conditions:
1. On success: returns a non-null Graphics_Window*. Exactly one slot in graphics_windows is transitioned from deallocated to allocated (serialization header UUID set to the resolved UUID via ALLOCATE_P). The window's width_of__graphics_window__u32 and height_of__graphics_window__u32 are set from the texture flags. The window's p_PLATFORM_gfx_window is set. The window's default compose/render function pointers and UUID fields are set to defaults by initialize_graphics_window. The window is stored in one NULL slot of ptr_array_of__sorted_graphic_windows. The array is re-sorted in-place by sort_graphic_windows_in__graphic_window_manager.
2. On pool-full (graphics_windows full): returns 0 and emits a debug_error. No state is mutated.
3. On sorted-slot-full: calls debug_abort and returns 0. (debug_abort may terminate the process, making the return unreachable.)
4. On platform window allocation failure: returns 0, emits a debug_error, and calls DEALLOCATE_P on the slot (effectively a no-op at this point since ALLOCATE_P has not yet been called — the slot remains in its pre-existing deallocated state). No slot is registered in the sorted array.

Correctness Verdict: Incorrect

Semantic Alignment:
The core allocation flow — UUID resolution, slot acquisition, platform window acquisition, struct initialization, field population, sorted-array registration, and re-sorting — is logically correct and matches the function's intent. However, there is a critical flag-overwrite ordering bug in the state-flag manipulation:

- Line 170-171: set_graphics_window_as__in_need_of__composition OR's in GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY (BIT 1) into graphics_window__flags.
- Line 177-179: graphics_window__flags = texture_flags_for__gfx_window OVERWRITES the entire field, destroying the COMPOSE_DIRTY flag (and potentially other state flags) set moments earlier.
- Line 181-182: set_graphics_window_as__enabled OR's in GRAPHICS_WINDOW__FLAG__IS_ENABLED (BIT 0).

The texture flags (uint32_t) encode their height dimension in bits 0-2 and width dimension in bits 3-5 (TEXTURE_FLAG__LENGTH__BIT_COUNT = 3, MASK = 0b111). The graphics_window__flags field is a uint8_t (Graphics_Window_Flags__u8) whose bits 0-2 are used for IS_ENABLED (BIT 0), COMPOSE_DIRTY (BIT 1), and IS_PLATFORM_PROVIDED (BIT 2). These bit ranges overlap.

This causes two problems:
(a) The COMPOSE_DIRTY flag set at line 170-171 is unconditionally destroyed by the assignment at line 177-179. Only IS_ENABLED is re-applied at line 181-182. As a result, newly allocated windows do not have COMPOSE_DIRTY set, and may not be composited on their first frame (see is_graphics_window_in_need_of__composition at graphics_window.c:409 and compose_graphic_windows_in__graphics_window_manager at graphics_window_manager.c:780, which skip windows lacking this flag).
(b) For texture dimensions where the height enum is non-zero (e.g., x16, x32, x64, x128, x256, x512, x1024), the texture flag value's bits 0-2 overlap with and corrupt the window state flags. For example, a 64x64 texture flag has value 27 (0b11011), which would set IS_PLATFORM_PROVIDED (BIT 2) to 1, causing is_graphics_window__platform_provided to incorrectly return true for non-platform-provided windows.

The texture dimension information is already stored separately in width_of__graphics_window__u32 (set at lines 164-166) and height_of__graphics_window__u32 (set at lines 167-169). The assignment of texture_flags_for__gfx_window to graphics_window__flags at lines 177-179 serves no useful purpose for dimension tracking and corrupts the state flags. The fix is to remove that assignment entirely, or at minimum move it before the set_graphics_window_as__in_need_of__composition and set_graphics_window_as__enabled calls and apply it with care for bit overlap — but simply removing it is the correct fix since the dimensions are already captured.

Implementation Correctness:
- Type compatibility: The assignment graphics_window__flags = texture_flags_for__gfx_window converts Texture_Flags (uint32_t) to Graphics_Window_Flags__u8 (uint8_t). For valid texture flags (using only bits 0-5), truncation to 8 bits does not lose dimension data, but the semantic bit overlap with window state flags is the bug described above. The width/height assignments (Quantity__u16 to Quantity__u32) are safe widening conversions with no truncation.
- Undefined behavior: No pointer arithmetic beyond bounded array indexing. No null dereferences — p_graphics_window__available is checked for null (line 128) before any field access; p_ptr_sorted_graphics_window_slot is checked for null (line 138) before dereferencing; p_PLATFORM_gfx_window is checked for null (line 152) before use. The DEALLOCATE_P macro accesses ->size_of__struct which is guaranteed valid because initialize_serialization_header__contiguous_array set it during manager initialization.
- Validation: No null check on p_gfx_context or p_graphics_window_manager. This is consistent with the codebase convention where internal allocation functions defer validation to callers; the sole caller (allocate_graphics_window_with__uuid_from__graphics_window_manager at line 206, which delegates from the inline wrapper at graphics_window_manager.h:126) is expected to pass valid pointers. The debug_abort on sorted-slot exhaustion (line 139) correctly treats this as an unrecoverable internal inconsistency.
- Initialization semantics: The initialize_graphics_window call (line 158) performs Lavender-style initialization — it memsets the struct body after the Serialization_Header to zero and sets default function pointers and UUIDs. This is NOT RAII resource acquisition; no platform resources are claimed here. The actual resource (PLATFORM_graphics_window) is acquired separately at lines 143-150. This is consistent with Lavender's "initialization ≠ RAII" convention. allocate_graphics_window_with__uuid_from__graphics_window_manager at line 206 correctly delegates to this internal function.
- DEALLOCATE_P on the failure path (line 154) is effectively a no-op: at that point neither initialize_graphics_window nor ALLOCATE_P has been called, so the slot retains its pre-existing deallocated state (UUID = IDENTIFIER__UNKNOWN__u32). Calling DEALLOCATE_P is harmless but does not change any state.

Side Effects:
1. Mutates p_graphics_window_manager->graphics_windows: one deallocated slot is transitioned to allocated state — its serialization header UUID is set to the resolved UUID and size_of__struct is confirmed, via the ALLOCATE_P macro at lines 160-162.
2. Mutates p_graphics_window_manager->ptr_array_of__sorted_graphic_windows: one NULL slot is replaced with a pointer to the newly allocated Graphics_Window (line 184-185).
3. Calls sort_graphic_windows_in__graphic_window_manager (line 187-188): reorders the ptr_array_of__sorted_graphic_windows array in-place via heap_sort__opaque, using the priority-based comparison and swap callbacks.
4. May call PLATFORM_allocate_gfx_window (lines 146-149): acquires a platform-level graphics window resource, when no optional platform window is provided by the caller.
5. May emit diagnostics via debug_error (lines 130, 153) and debug_abort (line 139) on failure paths.
6. No other externally observable state is modified. The function does not read or write any game-scoped state beyond the graphics window manager.
