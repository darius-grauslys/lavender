PLATFORM_get_position_in__file — core/include/platform.h

**Implemented identically in:**
- sdl/source/serialization/sdl_filesystem.c (line 201)
- nds/source/serialization/nds_filesystem.c (line 369)
- no_gui/source/serialization/no_gui_filesystem.c (line 373)
- tests/core/source/PLATFORM.c (line 407, stub — always returns -1)

Note: the prior stub claimed "no implementation found"; implementations exist in all three platform backends and a test stub.

---

### 2. Semantic

Queries the current read/write cursor offset (in bytes) of an open file stream, returning it as a 32-bit unsigned index. The header documents that it "Returns -1 on error."

### 3. Pre-conditions

1. `p_file_handler` must point to a valid, open `FILE*` stream (the parameter is `void*` and is reinterpreted as `FILE*` internally).
2. The underlying stream must be a seekable/positionable file (e.g. not a pipe or unbuffered stream), otherwise `ftell` is undefined per the C standard.
3. In debug builds (`#ifndef NDEBUG`): `p_file_handler` is checked for null and the function aborts via `debug_abort` if null. In release builds this check is compiled out — see issues below.
4. `p_PLATFORM_file_system_context` is accepted but unused by every implementation; the contract imposes no effective requirement on it (though conceptually it should be a valid context).

### 4. Post-conditions

1. On success, returns the logical file position as `Index__u32` (the `long` result of `ftell`, narrowed to 32 bits — see Implementation Correctness).
2. The stream's cursor is not moved (`ftell` is a non-mutating query).
3. On the debug null-handler path, `debug_abort` → `PLATFORM_abort()` terminates the program (the trailing `return` is dead code).
4. The documented "returns -1 on error" cannot be reliably satisfied (see Verdict and Implementation Correctness).

### 5. Correctness Verdict

**Incorrect**

The function violates its own documented contract: the return type `Index__u32` is unsigned (`uint32_t`), so the documented error sentinel "-1" is unrepresentable (it converts to `4294967295`). The validated error path returns `PLATFORM_Read_File_Error__Unknown` (= 3), which both contradicts the documented sentinel *and* is a valid, non-error file position (3), silently misreporting an error as a real offset. On the unvalidated path, `ftell`'s `-1L` failure becomes `UINT32_MAX`, which is inconsistent with the `3` returned on the validated path — so the error sentinel is not even self-consistent. In release builds the null check is compiled out, passing a null `p_file_handler` directly to `ftell()` (undefined behavior). Callers (inventory.c:61-64, inventory.c:96-99, global_space.c:165, global_space.c:247-250) never validate the return value against an error sentinel, so failures propagate as corrupt file positions. These are substantive correctness defects, not cosmetic.

### 6. Semantic Alignment

Partially aligned only on the happy path. `ftell()` correctly returns the current stream offset, matching the semantic intent to "get the position in file." However, the error semantic is fundamentally broken:

- The "Returns -1 on error" documentation is incompatible with the `uint32_t` return type — the function cannot return `-1`.
- The error sentinel actually produced on the null path is the `PLATFORM_Read_File_Error` enum constant `Unknown` (= 3), which is a different category entirely and is a legitimate file position, so an error is indistinguishable from a successful small offset.
- The implementation's error handling therefore does *not* fulfill the documented semantic, which requires a distinguishable error value. Per the guide, this is a semantic-alignment failure: the implementation is bugged and does not do its documented intention.

### 7. Implementation Correctness

- **Type compatibility: FAIL.** `ftell()` returns `long` (signed, commonly 64-bit). It is returned through an `Index__u32` (`uint32_t`) parameter, silently narrowing the value and converting `-1L` to `UINT32_MAX`. Any file position exceeding ~4 GiB is truncated. The error path additionally returns a `PLATFORM_Read_File_Error` enum (`Unknown`, value 3) into a `uint32_t` return — a category/misuse mismatch.
- **Undefined behavior: FAIL.** The null `p_file_handler` guard is `#ifndef NDEBUG`. With `NDEBUG` defined (release), a null `p_file_handler` is forwarded to `ftell()`, which has undefined behavior for a null `FILE*`. The `p_PLATFORM_file_system_context` pointer is never validated.
- **Validation appropriateness: INAPPROPRIATE.** The function's role is a thin `ftell` wrapper, so null-guard validation is reasonable — but it is only active in debug, leaving release unsafe. The test stub (tests/core/source/PLATFORM.c:407) returns `-1` (→ `UINT32_MAX`), which actually matches the *documented* contract better than the real implementations (which return 3). The implementations and the stub disagree on the error sentinel.
- **Dead code / missing `noreturn`:** `debug_abort` is declared `void` and is not marked `noreturn`, even though `debug_abort` → `PLATFORM_abort()` → `abort()` never returns. The `return PLATFORM_Read_File_Error__Unknown;` following `debug_abort(...)` is therefore unreachable in practice but remains, and its value is wrong regardless.
- **Copy-paste defect:** The abort message reads `"SDL::/NDS::/NO_GUI::PLATFORM_read_file, p_file_handler is null."` — it names `PLATFORM_read_file` instead of `PLATFORM_get_position_in__file`. The identical mislabel appears in `PLATFORM_set_position_in__file` as well.

### 8. Side Effects

- The `ftell()` call is a pure position query and does not modify the stream cursor or any observable file state; on the happy path the function is observationally pure.
- Conditional side effect on the debug error path: `debug_abort` → `PLATFORM_pre_abort()` + `PLATFORM_abort()`, which prints an error message and terminates the process (and may emit a core dump). The subsequent `return` statement is dead code.
- The function performs no allocations, performs no writes to the file or context, and does not mutate `p_PLATFORM_file_system_context`.
