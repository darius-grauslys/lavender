# Planning: game_directory.h — Incorrect Modules

**Review source:** `agents/core/review/include/serialization/game_directory.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/serialization/game_directory.h`
- `core/source/serialization/game_directory.c`
- `tests/core/source/serialization/test_suite_serialization_game_directory.c`
- `core/include/core_string.h` / `core/source/core_string.c` (`strncpy_returns__strlen`)
- `core/include/platform.h` / `core/include/platform_defaults.h` (`IO_path`, `MAX_LENGTH_OF__IO_PATH` = 128, `PATH_SEPERATOR` = `/`)
- `sdl/source/serialization/sdl_filesystem.c` (`PLATFORM_append_base_directory_to__path`)
- `no_gui/source/serialization/no_gui_filesystem.c` (`PLATFORM_append_base_directory_to__path`)

---

## 1. Problem Identification

### `append_path` — `core/source/serialization/game_directory.c` (lines 33–46)

The function violates its specified `Postcondition`s: it unconditionally writes a `PATH_SEPERATOR` and then copies `p_appended_path` verbatim via the standard `strncpy` (which provides no null-termination guarantee), without normalizing leading separators, handling empty inputs, or restoring the `Representation Invariant` of `IO_path`.

- **Double separator (`Surface-form leakage` / `Translation Gap`):** When `p_appended_path` begins with `/` (e.g. "/saves"), the inserted separator plus the suffix's own leading `/` produce "//". Test `game_directory__append_path_concatenates` expects "/home/user/saves".
- **Empty suffix trailing separator (`Boundary Condition`):** When `p_appended_path` is empty, a trailing `PATH_SEPERATOR` is still written, yielding "/home/user/" instead of the unchanged "/home/user". Test `game_directory__append_path_empty_suffix`.
- **Empty base leading separator (`Boundary Condition`):** When `p_path` is empty (length 0), a leading separator is written before the suffix, yielding "//saves" instead of "/saves". Test `game_directory__append_path_empty_base`.
- **Missing null-termination (`Representation Invariant`):** Standard `strncpy` provides no null-termination guarantee when the source length ≥ count. If `p_appended_path` fills the remaining buffer (`MAX_LENGTH_OF__IO_PATH - length_of__path - 1`), `p_path` ceases to be a valid C string, breaking the `Representation Invariant` of `IO_path` and causing undefined behavior in all subsequent `strnlen` / `strlen` / comparison operations.

### `stat_game_data_file` — `core/source/serialization/game_directory.c` (lines 7–30)

The function mixes path construction, buffer management, and filesystem `access()` with no `Boundary Condition` checks, risking a buffer overflow and unsigned integer underflow.

- **Unchecked separator write / buffer overflow (`Boundary Condition` / `Representation Invariant`):** After `PLATFORM_append_base_directory_to__path` populates `buffer`, the code unconditionally executes `buffer[index_of__path_append++] = '/'` with no `Precondition` check that `index_of__path_append < MAX_LENGTH_OF__IO_PATH`. If the base directory fills the buffer to capacity (128 bytes), this write is out of bounds.
- **Unsigned integer underflow (`Conservation Law` / `Boundary Condition`):** `MAX_LENGTH_OF__IO_PATH - index_of__path_append` is unsigned; once `index_of__path_append ≥ 128` (after the unchecked '/' write), the subtraction underflows to ~4.29 billion, causing `strncpy_returns__strlen` to write "game_data" far past the buffer. This violates the `Conservation Law` of the fixed-size buffer.
- **Sentinel / `Mode Confusion` in return value:** The function returns `Index__u32` (uint32_t) but uses `false` (0) as a `Sentinel` for "not found," conflating boolean and integer semantics. A return of 0 is indistinguishable from a valid zero-length path.

---

## 2. Impact Assessment

### `append_path`
- **Test suite:** `tests/core/source/serialization/test_suite_serialization_game_directory.c` includes `game_directory.c` directly (`#include <serialization/game_directory.c>`) and contains three tests that assert on the *correct* behavior. These tests currently fail. The fix will make them pass — no test assertion changes are required; the tests already encode the intended `Postcondition` contract.
- **Production callers:** No production callers of `append_path` were found in `./include` or `./source` (core, sdl, nds, no_gui). The function appears to be a utility not yet wired into the save/load pipeline. Correcting it therefore has no cascading caller impact.
- **Coupling note:** Because the test file `#include`s the `.c` directly, the tests are tightly `Coupled` to the implementation unit; the fix is behavior-preserving with respect to the test contract.

### `stat_game_data_file`
- **Production callers:** No callers of `stat_game_data_file` were found in `./include` or `./source`. It is not yet invoked by the save/load flow.
- **Dependency — `PLATFORM_append_base_directory_to__path`:** This function is implemented (identically) in `sdl/source/serialization/sdl_filesystem.c` and `no_gui/source/serialization/no_gui_filesystem.c`. Both implementations use `strncpy(..., MAX_LENGTH_OF__IO_PATH)` — the *full* buffer count rather than `MAX_LENGTH_OF__IO_PATH - *p_index_of__path_end` — which is itself a latent `Boundary Condition` that compounds the overflow risk in `stat_game_data_file`. Correcting `stat_game_data_file` to add bounds checks will expose this latent assumption in the platform layer; the platform implementation should also be hardened to respect remaining buffer capacity.
- **Return-value contract:** If the `Sentinel` is changed (e.g. to a distinct error code or out-parameter), any future caller must adopt the new contract. Since no callers exist yet, this is safe to revise now.

---

## 3. Resolution Assessment

### `append_path`
1. **Guard the empty-suffix case:** If `p_appended_path` is empty (length 0), return without writing anything — satisfies the `Postcondition` that the path remains unchanged.
2. **Guard the empty-base case:** If `p_path` is empty, copy `p_appended_path` directly (stripping any leading separator if present) without prepending a separator.
3. **Avoid double separators:** When both base and suffix are non-empty, insert a single `PATH_SEPERATOR` only if the suffix does not already begin with one (normalize the junction).
4. **Guarantee null-termination:** After the copy, explicitly write `'\0'` at the computed end position (clamped to `MAX_LENGTH_OF__IO_PATH - 1`) to restore the `Representation Invariant` of `IO_path`. Prefer `strncpy_returns__strlen` (which returns the copied length and null-terminates when the source fits) over raw `strncpy`, or add an explicit terminator.
5. **No caller updates needed** (no production callers; tests already assert correct behavior).

### `stat_game_data_file`
1. **Add bounds check before separator write:** Before `buffer[index_of__path_append++] = '/'`, verify `index_of__path_append + 1 < MAX_LENGTH_OF__IO_PATH`. If insufficient capacity remains, return the not-found sentinel (or an error code) without writing out of bounds.
2. **Guard the `strncpy_returns__strlen` length:** Compute remaining capacity as `MAX_LENGTH_OF__IO_PATH - index_of__path_append` only after confirming `index_of__path_append < MAX_LENGTH_OF__IO_PATH`, preventing unsigned underflow.
3. **Resolve the `Sentinel` / `Mode Confusion`:** Change the return type or contract so "not found" is not conflated with a valid length-0 path. Options: (a) return a distinct error sentinel distinct from any valid path length, or (b) use an out-parameter for the path length and return a bool. Since no callers exist, this can be revised freely.
4. **Harden the platform dependency:** Update `PLATFORM_append_base_directory_to__path` (sdl and no_gui) to use `MAX_LENGTH_OF__IO_PATH - *p_index_of__path_end` as the `strncpy` count, so the platform layer respects remaining buffer capacity and does not compound the overflow.
5. **No caller updates needed** (no production callers; no existing tests).

---

## 4. Test Verification Checklist

- **Existing tests (`append_path`):** Three tests in `test_suite_serialization_game_directory.c` assert the *correct* behavior (`game_directory__append_path_concatenates`, `game_directory__append_path_empty_suffix`, `game_directory__append_path_empty_base`). They will pass once the implementation is fixed. No assertion changes required.
- **Missing tests (`stat_game_data_file`):** No tests exist for `stat_game_data_file`. New tests are needed:
  - `Property Based Testing` — verify the constructed path is always null-terminated and within `MAX_LENGTH_OF__IO_PATH` for varying base-directory lengths (including the capacity-boundary case).
  - `Fuzzing` — feed base directories of length approaching `MAX_LENGTH_OF__IO_PATH` to exercise the overflow/underflow path.
  - `Round Trip Check` — if `append_path` is used to build the path, verify `stat_game_data_file` constructs `<base>/game_data` correctly.
  - `Golden-file Test` — assert the exact constructed path string against an expected golden value for a known base directory.
  - `Mutation Testing` — confirm the test suite would catch the double-separator and missing-null-terminator defects.
- **Blast radius (tests):** Low. The three `append_path` tests already encode the target contract. New tests for `stat_game_data_file` are additive. No phased test rollout required.

---

## 5. Blast Radius Summary

- **Files needing changes:** 1 source file (`core/source/serialization/game_directory.c`), 2 platform files (`sdl/source/serialization/sdl_filesystem.c`, `no_gui/source/serialization/no_gui_filesystem.c`), and 1 test file (additive tests only — no assertion changes). Optionally the header (`core/include/serialization/game_directory.h`) if the `stat_game_data_file` return contract is revised.
- **Behavior preservation:** `append_path` corrections align the implementation with the existing test contract — behavior is "corrected," not changed for current callers (none exist). `stat_game_data_file` corrections are defensive (bounds checks) plus a sentinel-contract revision; no callers exist to break.
- **Phased approach:** Not required. The blast radius is contained to one core module and its two platform backends.
- **De facto contracts invalidated:** The implicit assumption that `PLATFORM_append_base_directory_to__path` will never fill the buffer to capacity (relied upon by `stat_game_data_file`'s unchecked '/' write) is invalidated; the platform layer must be hardened in tandem.
