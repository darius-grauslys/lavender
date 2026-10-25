# PLATFORM_read_file

- **Function name:** `PLATFORM_read_file`
- **File of origin:** `core/include/platform.h` (declared, line 323)
  - Implementations (platform-dependent; core itself implements none — see `platform.h:14-15`):
    - `sdl/source/serialization/sdl_filesystem.c` (line 167) — strongest; emits `End_Of_File` on a zero-byte read
    - `nds/source/serialization/nds_filesystem.c` (line 333) — End_Of_File check is commented out; always returns `None`
    - `no_gui/source/serialization/no_gui_filesystem.c` (line 342) — no End_Of_File check at all; always returns `None`
  - Test stub: `tests/core/source/PLATFORM.c` (line 395) returns `PLATFORM_Read_File_Error__Unknown` unconditionally
  - Error enum: `core/include/defines_weak.h:224` (`None=0`, `End_Of_File=1`, `System_Busy`, `Unknown`)

## 2. Semantic

Reads `quantity_of__reads` blocks of `*p_length_of__data_to_read` bytes each from the open file identified by `p_file_handler` into `buffer`, and reports status via the returned `PLATFORM_Read_File_Error`. On output, `*p_length_of__data_to_read` is overwritten with the total number of bytes actually read (`fread`'s element count × the per-element size). Uses standard C `fread` semantics: `fread(destination, size, nmemb, p_file)` where `size = *p_length_of__data_to_read` and `nmemb = quantity_of__reads`.

## 3. Pre-conditions

1. `p_file_handler` must be a valid, open `FILE*` previously obtained from `PLATFORM_open_file` (representing a read-capable file). Null-checked only in debug builds (`#ifndef NDEBUG`); in release builds a null handler is dereferenced by `fread` (undefined behavior / segfault).
2. `destination` must point to a writable buffer of at least `*p_length_of__data_to_read * quantity_of__reads` bytes. Not validated by the function — caller's responsibility.
3. `p_length_of__data_to_read` must be non-null; it is dereferenced unconditionally. This is **not** validated on any backend (not even in debug builds) — a null pointer is a null-dereference (undefined behavior).
4. `p_PLATFORM_file_system_context` is accepted for API-convention consistency but is **unused** by all backends; it may be null or non-null without effect.
5. `length_of__data` (`*p_length_of__data_to_read`) and `quantity_of__reads` are not validated; zero values produce a no-op `fread` (writes nothing) that returns element count 0, which on SDL yields `End_Of_File`.
6. The file must have been opened in a read-capable mode by `PLATFORM_open_file`; this function performs no mode validation.

## 4. Post-conditions

1. On all backends, `*p_length_of__data_to_read` is set to `fread_element_count × original_size`, i.e. the total number of bytes actually read (this is the documented output contract and is wired correctly everywhere).
2. `destination` is filled with the bytes actually read, up to the amount reported in `*p_length_of__data_to_read`; the file stream position is advanced by that many bytes.
3. `destination`, `p_PLATFORM_file_system_context`, and all Lavender engine state are otherwise left unmodified.
4. **Defect (see Correctness Verdict):** the return-value (status) post-condition is backend-inconsistent. SDL returns `PLATFORM_Read_File_Error__End_Of_File` when zero bytes are read and `None` otherwise. The NDS and no_gui backends **always return `None`** — the NDS End_Of_File check is explicitly commented out (`nds/source/serialization/nds_filesystem.c:357-364`) with a TODO referencing `PLATFORM_write_file`'s identical gap, and no_gui has no such check at all. No backend ever returns `System_Busy`.
5. A partially-successful read (0 < elements_read < nmemb) leaves `*p_length_of__data_to_read` at the true bytes-read total and returns `None` (success). Short reads are therefore *not* signalled as errors; consumers must inspect the output length to detect them (the intended contract, e.g. `entity/entity.c:338` checks `if (error)`, while `world/world.c:311` has a TODO to verify read lengths).

## 5. Correctness Verdict

**Incorrect**

The core read operation itself is wired correctly on every backend (`fread` is called with the proper argument order, and the bytes-read output is computed correctly as `element_count × per_element_size`). However, the function **does not consistently fulfill its error-reporting contract**, which is the purpose of the `PLATFORM_Read_File_Error` return value:

- On the NDS backend the End_Of_File check is commented out, so the function always returns `None` even on EOF.
- On the no_gui backend the End_Of_File check is absent entirely, so it also always returns `None`.
- No backend ever returns `PLATFORM_Read_File_Error__System_Busy` (the enum exists for this purpose but is never produced).

The net effect is that callers which rely on `if (error)` to detect read failures (e.g. `core/source/entity/entity.c:338`, the `m_entity_deserialization_handler__default` path reviewed alongside this function) cannot detect EOF on the NDS/no_gui backends, and the `End_Of_File` enum value is effectively dead on 2 of 3 real backends. The defect is the same class as the one flagged for `PLATFORM_write_file` (the sibling write primitive unconditionally returns `None` and discards `fwrite`'s return) and is called out in the codebase's own TODOs.

## 6. Semantic Alignment

**Partially failed.** The read primitive and the bytes-read output match the semantic intent (correct primitive, correct arguments, correct units). The *status-reporting* half of the semantic contract is **not** fulfilled consistently: the intent includes surfacing `End_Of_File` (and the enum reserves `System_Busy` for busy/locked-file conditions), yet two of three backends unconditionally return `None` and none ever returns `System_Busy`. The SDL implementation is the lone exception and alone approaches the intended contract; the NDS and no_gui backends do not. This is not a drift in the computation but a failure to implement the status-propagation portion of the declared intent.

## 7. Implementation Correctness

- **Type compatibility:** `Quantity__u32` (`uint32_t`) is passed to `fread`'s `size_t` size/count parameters — safe widening (`size_t >= 32` bits on all targets). `fread`'s `size_t` return (element count) is stored in `Quantity__u32` — a narrowing conversion, but not a practical hazard for serialization-sized reads. `(u8*)` casts at call sites (e.g. `world.c:306`, `entity.c:333`) match the `u8 *destination` parameter. `void *` `p_file_handler` is assigned to `FILE *` — the conventional type-erased handle pattern used across this layer.
- **Undefined behavior:** No pointer arithmetic, no type punning, no out-of-bounds access. The multiplication `size_of__read * *p_length_of__data_to_read` is in `uint32_t` arithmetic and could overflow for extremely large reads, but this is not a realistic concern for Lavender's serialization records. Two genuine UB risks are not guarded: (a) `p_file_handler` null-dereference in release builds (`#ifndef NDEBUG` strips the check), and (b) **null `p_length_of__data_to_read`** — dereferenced on every backend without even a debug check.
- **Validation:** Appropriate for a thin platform wrapper (minimal, with a debug-only null check on the file handler), but inconsistent with the project's own convention for `PLATFORM_*` functions: `p_file_handler` gets a debug null guard while `p_length_of__data_to_read` — which is dereferenced unconditionally — does not. This null gap is shared by `PLATFORM_write_file` only nominally (its `length_of__data` is passed by value and not dereferenced).
- **Backend parity defect (distinct from the write-file sibling):** the three real backends diverge in status reporting. SDL emits `End_Of_File` on a zero-byte read; NDS has the equivalent check commented out; no_gui has no check. This makes `PLATFORM_read_file`'s return value non-portable across the supported backends and is the concrete failure behind the verdict.
- **Minor inconsistency:** the NDS implementation names the parameter `p_destination` while the SDL and no_gui implementations name it `destination` — no behavioral effect, purely cosmetic.

## 8. Side Effects

- **Mutates** the open file's stream position for the file referenced by `p_file_handler` (via `fread`), and writes read bytes into `destination`. This is the function's primary, intended side effect.
- **Mutates** `*p_length_of__data_to_read` (overwrites the input size with the total bytes-read count).
- In **debug builds only**, a null `p_file_handler` triggers `debug_abort(...)` (a fatal debug handler) followed by a guarded `return PLATFORM_Read_File_Error__Unknown`. No backend performs a debug check on `p_length_of__data_to_read`, so a null value yields undefined behavior (null dereference) rather than a guarded abort.
- Does not modify `p_PLATFORM_file_system_context` or any Lavender engine state directly; out-of-scope callee side effects originate only from `fread` itself (file-position advancement, possible OS read).
