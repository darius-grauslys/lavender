## 1. Header
- **Function name:** `PLATFORM_get_provided_windows`
- **File of origin:** `core/include/platform.h` (declaration, line 217). Concrete implementation reviewed: `sdl/source/rendering/sdl_gfx_window_manager.c` (lines 51-84). The test stub in `tests/core/source/PLATFORM.c:261` is a no-op returning 0.

## 2. Semantic
Fills a caller-provided buffer with pointers to platform-provided graphics windows (alongside matching texture flags), returning the count of windows omitted due to buffer overflow. Supports pagination across sequential calls via an offset index that skips already-acquired windows.

## 3. Pre-conditions
1. `p_gfx_context` must be non-null and point to an initialized graphics context (it is dereferenced transitively by `PLATFORM_allocate_gfx_window` on the first call; the parameter is not itself validated by this function).
2. `ptr_array_of__PLATFORM_graphics_windows` must be a non-null pointer to a buffer of at least `quantity_of__ptrs_in_buffer__u32` elements of type `PLATFORM_Graphics_Window*` (it is written via `memset` and indexed at `[0]`).
3. `array_of__texture_flags` must be a non-null pointer to a buffer of at least `quantity_of__ptrs_in_buffer__u32` elements of type `Texture_Flags` (indexed at `[0]`).
4. `quantity_of__ptrs_in_buffer__u32` must equal the capacity of the caller's buffers. Must be >= 1 for any window pointer/flag pair to be written (a value of 0 yields the early return in pre-condition 6).
5. `index_of__offset__u32` is an offset into the platform's ordered list of provided windows; it must be >= 0 and ideally less than the total window count so that further windows remain to be filled.
6. If `quantity_of__ptrs_in_buffer__u32 == 0`, the function returns `1` immediately and performs no writes.

## 4. Post-conditions
1. If `quantity_of__ptrs_in_buffer__u32 == 0`: returns `1` and writes nothing.
2. Otherwise, the entire `ptr_array_of__PLATFORM_graphics_windows` buffer is zeroed via `memset` and then `buffer[0]` is set to the (possibly null) cached backbuffer pointer.
3. `array_of__texture_flags[0]` is set to a `Texture_Flags` value of `TEXTURE_FLAGS(TEXTURE_FLAG__SIZE_256x256, 0, TEXTURE_FLAG__FORMAT__RGBA8888)`.
4. Returns `0`.
5. The file-scope global `_p_PLATFORM_gfx_window__backbuffer` is lazily allocated on the first call (via `PLATFORM_allocate_gfx_window`) and cached; subsequent calls reuse it.

## 5. Correctness Verdict
**Incorrect**

## 6. Semantic Alignment
The documented contract (the header comment at `platform.h:205-216` and `agents/platform_api.md:354`) describes a multi-window pagination/overflow API: starting at `index_of__offset__u32`, copy up to `quantity_of__ptrs_in_buffer__u32` window pointers into the buffer, and return the count of available windows omitted due to insufficient buffer capacity. The header example ("for buffer size 8 ... call 1 -> index:0, returns 5 (8/13 windows acquired); call 2 -> index:8, returns 0 (last 5 acquired)") makes this intent explicit.

The SDL implementation fails to honor this contract:
- The `index_of__offset__u32` parameter is **completely ignored** (never referenced in the body). Pagination is not implemented; a call with a nonzero offset does not skip already-acquired windows.
- Only a single window (the lazily-allocated "backbuffer") is ever exposed, despite `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` being 128 for the SDL backend. The function never iterates over or reports more than one window.
- The overflow return value is wrong: it returns `0` whenever the buffer is non-empty and `1` only when the buffer size is 0. It never computes an actual omission count based on available windows vs. capacity/offset, so overflow can never be reported correctly.

As a result, a caller relying on the documented offset/overflow semantics (e.g., `graphics_window_manager.c:926-934`, which loops calling this function with an advancing offset, accumulating overflow) would receive the same single window repeatedly rather than distinct windows, and would never observe an overflow condition. The implementation does **not** fulfill the documented semantic intent.

## 7. Implementation Correctness
- **Type compatibility:** Parameter types match the declaration exactly. `Quantity__u32` and `Index__u32` are both `uint32_t` (`defines.h:129,140`). `memset` uses `sizeof(PLATFORM_Graphics_Window*) * quantity_of__ptrs_in_buffer__u32`, which is the correct element size for the pointer array. No implicit conversions or truncation.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference within this function, no type punning, no out-of-bounds access. The early `if (!quantity_of__ptrs_in_buffer__u32) return 1;` guarantees `quantity >= 1` before indexing `[0]` on both output buffers, so the `[0]` writes are in-bounds. The file-scope global `_p_PLATFORM_gfx_window__backbuffer` is initialized to `0` (`sdl_gfx_window_manager.c:33`), so the first-call null check is well-defined. If `PLATFORM_allocate_gfx_window` returns null, `buffer[0]` remains null (set by the prior `memset`); the caller (`graphics_window_manager.c:945`) handles a null entry by breaking, so null propagation is safe.
- **Validation:** Validation is minimal but consistent with the function's role: it guards the buffer-capacity edge case (returns early on a zero-length buffer) and relies on the caller to supply valid, sufficiently-sized buffers and a valid `p_gfx_context`. This matches the documented contract, where the caller owns the buffers. The unused `index_of__offset__u32` is not undefined behavior, but its absence is a semantic (not UB) defect; some compilers may emit an unused-parameter warning.
- No issues with strict-aliasing, alignment, or sequence points.

## 8. Side Effects
- **Mutates** the caller-provided array `ptr_array_of__PLATFORM_graphics_windows`: the entire buffer is zeroed via `memset`, then the cached backbuffer pointer is written to index `0`.
- **Mutates** the caller-provided array `array_of__texture_flags`: the value `TEXTURE_FLAGS(TEXTURE_FLAG__SIZE_256x256, 0, TEXTURE_FLAG__FORMAT__RGBA8888)` is written to index `0`.
- **Stateful persistent side effect:** on the first invocation, lazily allocates a single `PLATFORM_Graphics_Window` (the "backbuffer") via `PLATFORM_allocate_gfx_window(p_gfx_context, texture_flags)` and caches the pointer in the file-scope global `_p_PLATFORM_gfx_window__backbuffer`. This allocation calls into the SDL sub-context's `f_SDL_allocate_gfx_window` function pointer, creating platform graphics resources. All subsequent invocations reuse the cached pointer without re-allocating.
- **Callee side effects (out of scope, noted for completeness):** `PLATFORM_allocate_gfx_window` allocates a platform graphics window resource and invokes the SDL window-creation function pointer; these are downstream of, and triggered by, this function's first call.
