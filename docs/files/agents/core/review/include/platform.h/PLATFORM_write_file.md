# PLATFORM_write_file

- **Function name:** `PLATFORM_write_file`
- **File of origin:** `core/include/platform.h` (declared, line 316)
  - Implementations:
    - `sdl/source/serialization/sdl_filesystem.c` (line 144)
    - `nds/source/serialization/nds_filesystem.c` (line 298)
    - `no_gui/source/serialization/no_gui_filesystem.c` (line 319)
  - Test stub: `tests/templates/source/PLATFORM.c` (line 386) returns `PLATFORM_Write_File_Error__Unknown`

## 2. Semantic

Writes `quantity_of__writes` blocks of `length_of__data` bytes each from `source` into the open file identified by `p_file_handler`, using `fwrite`, and reports success/failure via the returned `PLATFORM_Write_File_Error`. The total number of bytes written is `length_of__data * quantity_of__writes` (standard C `fwrite` semantics).

## 3. Pre-conditions

1. `p_file_handler` must be a valid, open `FILE*` previously obtained from `PLATFORM_open_file` (representing a writable file). Null-checked only in debug builds (`#ifndef NDEBUG`); in release builds a null handler is dereferenced by `fwrite` (undefined behavior / segfault).
2. `source` must point to a readable buffer of at least `length_of__data * quantity_of__writes` bytes. Not validated by the function — caller's responsibility.
3. `p_PLATFORM_file_system_context` is accepted for API-convention consistency but is **unused** by this function; it may be null or non-null without effect.
4. `length_of__data` and `quantity_of__writes` are not validated; a zero value produces a no-op `fwrite` (writes zero items) and still returns `__None`.
5. The file must have been opened in a write-capable mode by `PLATFORM_open_file`; this function performs no mode validation.

## 4. Post-conditions

1. On the assumed success path, `length_of__data * quantity_of__writes` bytes have been appended/written to the file at the current stream position, and the file position is advanced by that many bytes.
2. `source`, `p_PLATFORM_file_system_context`, and all Lavender engine state are left unmodified (read-only inputs to the operation).
3. **Defect (see Correctness Verdict):** The function returns `PLATFORM_Write_File_Error__None` unconditionally and never inspects `fwrite`'s return value (`size_of__write`). There is no post-condition guarantee regarding error reporting — the function can return `__None` even when `fwrite` wrote fewer than `quantity_of__writes` items or failed outright.

## 5. Correctness Verdict

**Incorrect**

The write primitive itself is wired correctly (`fwrite` is called with the proper argument order), but the function cannot fulfill its declared error-reporting contract: the return value of `fwrite` is stored in a local (`size_of__write`) and then discarded. The function unconditionally returns `PLATFORM_Write_File_Error__None` regardless of whether the write succeeded, was short, or failed. This renders every caller-side `if (error)` check (e.g. `core/source/entity/entity.c:255`, `:268`, `:282`) dead code, so write failures during serialization are silently swallowed and save files can be corrupted without detection. The `PLATFORM_Write_File_Error` enum (`defines_weak.h:217`) exists specifically to signal `Max_Size_Reached`, `System_Busy`, and `Unknown`, none of which are ever produced here.

The defect is identical across all three real implementations (sdl, nds, no_gui). The NDS implementation even contains a commented-out TODO documenting the gap (`nds/source/serialization/nds_filesystem.c:318-328`), where the intended comparison `size_of__write < length_of__data * quantity_of__writes` → `PLATFORM_Write_File_Error__Max_Size_Reached` was disabled because `fwrite` anomalously returns 1 on that backend (libfat), and the underlying cause was never resolved.

## 6. Semantic Alignment

**Partially failed.** The write operation matches the semantic intent (correct primitive, correct arguments, correct units). However, the *error-reporting* half of the semantic contract is not fulfilled: the function is unable to signal any failure condition. Per the guide, this is a case where the implementation is bugged and does not fulfill its full intention — the intent includes reporting write status via the returned enum, and that intent is not met. A consumer cannot distinguish a successful full write from a partial or failed write, which breaks the serialization pipeline's ability to fail safely.

## 7. Implementation Correctness

- **Type compatibility:** `Quantity__u32` (`uint32_t`) is passed to `fwrite`'s `size_t` size and count parameters — safe widening on all realistic targets (`size_t >= 32` bits). `fwrite`'s `size_t` return is stored into `Quantity__u32` — a technically narrowing conversion, but not a practical risk for serialization-sized writes. No implicit-conversion truncation hazards on the arguments themselves.
- **Undefined behavior:** No pointer arithmetic, no type punning, no out-of-bounds access. The sole UB risk is dereferencing a null `p_file_handler` in release builds (and a null `source`), because these checks are gated behind `#ifndef NDEBUG`. This is an intentional debug-vs-release trade-off consistent with surrounding `PLATFORM_*` functions (e.g. `PLATFORM_read_file`, `PLATFORM_get_position_in__file`), but it is inconsistent that `p_file_handler` is null-guarded while `source` is not.
- **Validation:** Appropriate for a thin platform wrapper — minimal validation, with debug-only null check on the file handler. `source` null-validation is arguably missing but is conventionally the caller's responsibility for this abstraction layer.
- **Dead code / unused:** `p_PLATFORM_file_system_context` is unused, but this follows the project's API convention (every `PLATFORM_*` function takes the context as the first parameter for consistency), so it is an intentional design choice, not a defect.

## 8. Side Effects

- **Mutates** the file's contents and stream position for the open file referenced by `p_file_handler` (via `fwrite`). This is the function's primary, intended side effect.
- In **debug builds only**, a null `p_file_handler` triggers `debug_abort(...)` (a fatal debug handler) followed by a guarded `return PLATFORM_Write_File_Error__Unknown`.
- Does not modify `source`, `p_PLATFORM_file_system_context`, or any Lavender engine state directly (out-of-scope callee side effects from `fwrite` itself are the only file-system mutation).
