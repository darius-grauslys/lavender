# PLATFORM_allocate_texture_with__path

## Header
- **Function name:** `PLATFORM_allocate_texture_with__path`
- **File of origin:** `core/include/platform.h` (declared at line 141)
- **Reference implementation:** `sdl/source/rendering/sdl_texture_manager.c:129` (delegates to `GL_allocate_texture_with__path`, `sdl/source/rendering/opengl/gl_texture.c:111`). Stubs in `no_gui/source/NOT_IMPL.c:25` and `tests/templates/source/PLATFORM.c:232` return `0` (true/failure).
- **Signature:**
  ```c
  bool PLATFORM_allocate_texture_with__path(
          PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
          PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
          Texture_Flags texture_flags,
          const char *c_str__path,
          Texture *p_OUT_texture);
  ```

## Semantic
Allocates a platform/GPU texture and loads image pixel data from the file located at `c_str__path` into that texture, storing the resulting handle in `p_OUT_texture`. Returns `true` if any step fails, `false` on success. (Per the header comment "returns true if failure.")

## Pre-conditions
1. `p_PLATFORM_gfx_context` is non-null and points to a valid, already-initialized platform graphics context (it provides the rendering backend/sub-context).
2. `c_str__path` is non-null, a NUL-terminated C string, and refers to a readable image file supported by the backend's image loader.
3. `p_OUT_texture` is non-null and points to valid caller-owned storage (`Texture` struct) into which the platform handle will be written.
4. `texture_flags` is a valid flag set; its encoded length/height/channel semantics determine the requested channel count (e.g. `SDL_PIXELFORMAT_*` format bits used to pick `requested_channels`).
5. In debug builds (`#ifndef NDEBUG`), non-null `p_PLATFORM_gfx_context`, `c_str__path`, and `p_OUT_texture` are asserted; a violation causes an early `return true`.
6. The image loader (stbi) must be initialized/available (it is a global default in the SDL/GL backend).

## Post-conditions
1. On success (`false` return): `p_OUT_texture->p_PLATFORM_texture` holds the platform texture handle; `p_OUT_texture->texture_flags == texture_flags`; the image pixels have been uploaded to the GPU (e.g. via `glTexImage2D`); no pre-existing allocation is leaked.
2. On failure (`true` return): `p_OUT_texture->p_PLATFORM_texture` is null (the SDL wrapper returns `!p_PLATFORM_texture`; the GL layer returns `0` and releases any partially-allocated texture), while `texture_flags` is still written — so a failed call leaves the `Texture` in a null-handle state.
3. On `stbi_load` failure, the backing platform texture allocated by `GL_allocate_texture` is explicitly released (`SDL_release_texture`), so there is no resource leak; the caller's `Texture` ends with a null `p_PLATFORM_texture`.
4. Width/height/channel mismatches between the loaded image and the pre-allocated texture size are only emitted as debug warnings, not errors; the upload proceeds with the image's actual dimensions.
5. `p_OUT_texture` is mutated in place; `p_PLATFORM_gfx_context` and `c_str__path` are not modified by this function.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation fulfills the semantic intent. The SDL `PLATFORM_allocate_texture_with__path` wraps the sub-context's `f_SDL_allocate_texture_with__path`, which is bound to `GL_allocate_texture_with__path`. That function first allocates a backing platform texture via `GL_allocate_texture`, loads the image from `path` with `stbi_load`, and uploads the pixel data via `glTexImage2D`. On `stbi_load` failure it releases the backing texture and returns `0` (null), causing the wrapper to return `true`. The "allocate a texture from a file path" intent is satisfied end to end.

Note: the function is a platform API declared in a header and implemented per-backend; the SDL/GL backend is treated as the canonical reference. The no_gui and test-template backends are no-ops returning `true` (failure), which is consistent with their stub semantics.

## Implementation Correctness
- **Type compatibility:** The `bool` return matches the project-wide "true means failure" convention. Parameter types match the declaration exactly. The output writes target `Texture` fields (`PLATFORM_Texture *` at `defines.h:755` and `Texture_Flags` at `defines.h:756`) with no truncation or implicit conversion.
- **Undefined behavior:** No null dereference — debug guards in `sdl_texture_manager.c:136-147` check the three pointer params, and `GL_allocate_texture_with__path` null-checks `p_PLATFORM_texture` after `GL_allocate_texture` before use (`gl_texture.c:120`). `stbi_load` receives the caller-provided `path` string. No pointer arithmetic or out-of-bounds access occurs in the wrapper. `glTexImage2D` is called with the dimensions returned by the decoder.
- **Validation appropriateness:** Validation (non-null checks) is debug-only (`#ifndef NDEBUG`). Given this is a platform-boundary API invoked through the trusted core path (`load_texture_from__path_with__alias`, `aliased_texture_manager.c:168`, which builds `full_path` internally), debug-only validation is an acceptable design choice for a hot path.
- **Non-blocking issue:** `p_PLATFORM_gfx_window` is accepted as a parameter but is **not used** by the SDL/GL backend — allocation does not bind to a specific window. This is not a correctness bug (parameters may exist for cross-backend interface uniformity), but it is inert in the canonical backend. It does not cause undefined behavior.
- **Resource ownership:** On success, ownership of the platform texture transfers to the caller, who must later call `PLATFORM_release_texture`; on failure, the GL layer self-cleans (no leak). This matches the function's resource-creating role.

## Side Effects
- Mutates the `Texture` struct at `p_OUT_texture`: writes `p_PLATFORM_texture` (handle on success, null on failure) and `texture_flags`.
- Allocates a platform/GPU texture resource; on success, uploads image pixel data to the GPU (e.g. `glTexImage2D`); on `stbi_load` failure, releases the backing texture.
- Through the SDL/GL backend, invokes the global `stbi_set_flip_vertically_on_load(true)` prior to decoding, which mutates stb_image's global flip state (visible to any subsequent `stbi_load` calls in the same process until changed).
- Does not modify `p_PLATFORM_gfx_context` or `c_str__path`.
- Performs file I/O indirectly via stb_image (image decoding of the file at `path`).
