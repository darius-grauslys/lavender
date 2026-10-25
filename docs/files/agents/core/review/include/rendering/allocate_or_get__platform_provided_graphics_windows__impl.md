allocate_or_get__platform_provided_graphics_windows — core/source/rendering/graphics_window_manager.c (lines 908-986)

Iterates over platform-provided graphics windows via PLATFORM_get_provided_windows, allocating or retrieving a Graphics_Window for each, marking them as platform-provided, and writing them into the caller-supplied output buffer. Uses a do-while loop to handle overflow when the platform has more windows than the buffer can hold.

Pre-conditions:
1. p_gfx_context must be non-null; it is passed through to PLATFORM_get_provided_windows and _allocate_graphics_window_from__graphics_window_manager.
2. p_graphics_window_manager must be non-null and properly initialized (graphics_windows array with serialization headers set, ptr_array_of__sorted_graphic_windows zero-initialized, randomizer seeded).
3. ptr_array_of__graphics_windows must be non-null and point to a writable buffer of at least quantity_of__ptrs_in_buffer__u32 entries.
4. quantity_of__ptrs_in_buffer__u32 must be non-zero; otherwise VLAs of size 0 are undefined behavior and PLATFORM_get_provided_windows returns 1, causing an infinite loop.
5. p_quantity_of__overflowed_windows__u32 must be non-null; it is written to on both success and error paths.
6. offset_of__graphics_window is the starting index into the platform's window list; it may be 0 or any non-negative index.

Post-conditions:
1. On success (returns true): ptr_array_of__graphics_windows is zeroed, then filled with pointers to Graphics_Window objects corresponding to the platform-provided windows retrieved starting at offset_of__graphics_window. *p_quantity_of__overflowed_windows__u32 is set to the total number of windows omitted from the buffer across all PLATFORM_get_provided_windows calls (i.e., the total overflow count). Each retrieved Graphics_Window has GRAPHICS_WINDOW__FLAG__IS_PLATFORM_PROVIDED set.
2. On allocation failure (returns false): *p_quantity_of__overflowed_windows__u32 is set to 0. The state of ptr_array_of__graphics_windows is partially populated (zeroed then filled up to the point of failure). Previously allocated Graphics_Windows from earlier loop iterations remain allocated in the manager.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent — to retrieve all platform-provided windows in batches, allocating Graphics_Window wrappers as needed — is semantically sound. The do-while loop structure correctly retries when PLATFORM_get_provided_windows reports overflow. The use of get_p_graphics_window_with__this_PLATFORM_graphics_window to avoid duplicate allocation is correct. The goto assign_window pattern correctly skips allocation for windows that already have a Graphics_Window wrapper.

However, there is a critical bug in the offset calculation for subsequent calls to PLATFORM_get_provided_windows. Per the documentation in platform.h (lines 206-216):

  /// for buffer size 8
  /// call 1 -> index:0, returns 5 (8/13 windows acquired)
  /// call 2 -> index:8, returns 0 (last 5 acquired)

The return value of PLATFORM_get_provided_windows is the number of windows OMITTED due to overflow (not the number placed in the buffer). The offset for the next call must advance by the number of windows already retrieved (i.e., quantity_of__ptrs_in_buffer__u32 when the buffer is full due to overflow), not by the overflow count.

The code computes the offset as:
  offset_of__graphics_window + quantity_of__total_overflowed_windows__u32

where quantity_of__total_overflowed_windows__u32 accumulates the overflow counts. In the documented example with 13 windows and buffer size 8:
- Call 1: offset = 0 + 0 = 0, fills 8, returns 5. quantity_of__total_overflowed_windows__u32 = 5.
- Call 2: offset = 0 + 5 = 5. But the correct offset should be 8 (8 windows already retrieved).

This causes windows at indices 5-7 to be retrieved again (duplicates), while the output buffer from call 1 (containing windows 0-4) is overwritten by call 2's results (windows 5-12). Windows 0-4 are effectively lost from the output buffer. The caller, reset_platform_provided_graphics_windows, also propagates this bug: it increments index_of__current_acquisition by quantity_overflowed__u32 (the overflow count) rather than by the number of windows actually retrieved, compounding the error across calls to allocate_or_get__platform_provided_graphics_windows itself.

The fix is to track the number of windows placed in the buffer separately from the overflow count and use the former for the offset:
  offset_of__graphics_window + quantity_of__windows_placed_in__buffer__u32
where quantity_of__windows_placed_in__buffer__u32 is incremented by quantity_of__ptrs_in_buffer__u32 when overflow occurs (buffer is full), or by the actual count of non-null entries when no overflow occurs (though the loop exits in that case).

Implementation Correctness:
- Type compatibility: All parameter types match their target function signatures exactly. The expression offset_of__graphics_window + quantity_of__total_overflowed_windows__u32 is Index__u32 + Quantity__u32, both uint32_t, so no implicit conversion or truncation occurs. The VLA declarations use quantity_of__ptrs_in_buffer__u32 (Quantity__u32) as the size, which is valid in C.
- Undefined behavior: No pointer arithmetic beyond bounded array indexing. No null dereferences — ptr_array_of__graphics_windows is memset'd before use; p_graphics_window_possessing_this__PLATFORM_graphics_window is checked for null after both get_p_graphics_window_with__this_PLATFORM_graphics_window and _allocate_graphics_window_from__graphics_window_manager before any field access. The VLAs are stack-allocated and sized by the caller-supplied quantity, which is always non-zero in practice (callers pass MAX_QUANTITY_OF__GRAPHICS_WINDOWS or 1).
- Validation: No null checks on p_gfx_context, p_graphics_window_manager, ptr_array_of__graphics_windows, or p_quantity_of__overflowed_windows__u32. This is consistent with the codebase convention where internal functions defer validation to callers; all three callers pass valid pointers. No check for quantity_of__ptrs_in_buffer__u32 == 0, which would cause VLA size 0 (undefined behavior in C) and an infinite do-while loop (PLATFORM_get_provided_windows returns 1 for zero buffer size). This is a latent bug but not triggered by any current caller.
- The VLAs ptr_array_of__PLATFORM_graphics_windows and array_of__texture_flags are not zeroed between do-while iterations. The inner for-loop breaks on null entries (line 943: if (!p_PLATFORM_graphics_window) break), which relies on PLATFORM_get_provided_windows zeroing its output buffer. The SDL implementation does this (sdl_gfx_window_manager.c:60-63), but a platform implementation that does not zero the buffer could leave stale pointers from a previous iteration, causing the inner loop to process garbage. This is a portability concern but not a bug in the current SDL backend.

Side Effects:
1. Mutates ptr_array_of__graphics_windows: zeroed via memset at entry, then populated with Graphics_Window pointers during each do-while iteration. On the second and subsequent iterations, earlier entries are overwritten (this is the offset bug described above — entries from the first call are lost).
2. Mutates p_graphics_window_manager->graphics_windows: may transition deallocated slots to allocated state via _allocate_graphics_window_from__graphics_window_manager, which calls ALLOCATE_P to set the serialization header UUID.
3. Mutates p_graphics_window_manager->ptr_array_of__sorted_graphic_windows: _allocate_graphics_window_from__graphics_window_manager inserts new windows into the sorted pointer array and calls sort_graphic_windows_in__graphic_window_manager to re-sort.
4. Mutates Graphics_Window state: set_graphics_window_as__platform_provided OR's in GRAPHICS_WINDOW__FLAG__IS_PLATFORM_PROVIDED on each retrieved window.
5. May call PLATFORM_allocate_gfx_window (transitively via _allocate_graphics_window_from__graphics_window_manager) to acquire platform-level graphics window resources when no existing Graphics_Window possesses the platform window.
6. May emit diagnostics via debug_error on allocation failure (line 967).
7. No other externally observable state is modified.
