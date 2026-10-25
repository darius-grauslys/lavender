# util — Bitmap, hash_map (UUID pools), enum_map, and getter helpers

**Sources:** `core/source/util/bitmap/bitmap.c` + `core/include/util/bitmap/bitmap.h` + `core/include/util/hash_map/hash_map.h` + `core/include/util/enum_map/enum_map.h` + `core/include/util/getter/getter.h`

## Surface Concerns

The util module provides four data-structure families used throughout the engine as leaf primitives: bitmaps with optional heap overlays, UUID-keyed contiguous pools, enum-indexed arrays, and an empty getter placeholder. Every module in the engine may include these headers; the module calls no other engine modules and has no `platform.h` coupling except `bitmap.c` (which includes it).

- **Bitmap** — compact bitmask with O(1) set/get/is-bit operations on `u8` arrays, plus an optional logarithmic "heap" overlay (a 3^k-sized summary layout: N/8 + N/64 + N/512 + … bytes) for O(log N) first-set-bit search. `initialize_bitmap` fills all-set or all-clear. Heap overlay is accessed via `BITMAP_AND_HEAP` macro or the `SET_BIT_IN__BITMAP_AND_HEAP` convenience macro.
- **UUID-mapped pools** — `UUID_MAPPED__POOL` generates a struct containing a `Serialization_Pool` (defined in `defines.h`; see `serialization.md`) plus a flat array of a user-specified element type, each of which is expected to embed `Serialization_Header` as its first field. The companion `DECLARE_API__UUID_MAPPED__POOL` is a **broken template**: every generated body references the type name instead of the `p_name` parameter, and its dehash calls an undefined `DEHASH` macro, so it does not compile as written — and no in-repo code uses it. The working dehash path is `dehash_identitier_u32_in__contigious_array()` (see `serialization.md`), wrapped by `dehash_from__serialization_pool()` in `serialization/serialization_pool.h`.
- **Enum-indexed array** — `ENUM_MAP` generates a fixed-size array indexed by enum values, sized to `type_enum__Unknown` (the sentinel). `DEFINE_API__ENUM_MAP` also generates a `get_p_{type_value}_by__enum_key_from__{name}` pointer helper, and the bounds check plus the `_values[type_enum__None]` fallback on invalid keys are **debug-build only** — release builds index unchecked.
- **Getter** — currently empty (`getter.h` is a minimal placeholder).

## Public API Surface

### Key Types

**`Serialization_Pool`** — defined in `core/include/defines.h` (documented in `serialization.md`). Key members:
- `Serialization_Header *p_headers` — pointer to the contiguous array of headers.
- `Quantity__u32 quantity_of__pool_elements` — capacity in elements.
- `Quantity__u32 size_of__element` — byte size of each element struct.

### Key Functions

**Bitmap:**
- `void initialize_bitmap(u8 *p_bitmap, bool state, Quantity__u32 size_of__bitmap);` — fills bitmap all-set (`0xff`) or all-clear (`0x00`).
- `static inline bool is_bit_set_in__bitmap(u8 *p_bitmap, Quantity__u32 size_of__bitmap, Index__u32 index_of__bit);` — returns true if bit is set. O(1).
- `static inline void set_bit_in__bitmap(u8 *p_bitmap, Quantity__u32 size_of__bitmap, Index__u32 index_of__bit, bool state_of__bit);` — sets or clears a bit. O(1).
- `void set_bit_in__bitmap_and_heap(u8 *p_bitmap, u8 *p_end_of__heap, Quantity__u32, Index__u32, bool);` — sets a bit and propagates through the heap overlay.
- `Index__u32 get_index_of__first_set_bit_from__bitmap_and_heap(u8 *, Quantity__u32);` — returns first set-bit index via heap walk, or `INDEX__UNKNOWN__u32` if none. O(log N).
- `#define BITMAP(name, N)` / `#define BITMAP_AND_HEAP(name, N)` — declare bitmap / bitmap+heap arrays.
- `#define SET_BIT_IN__BITMAP_AND_HEAP(bitmap, size, index, state)` — convenience macro wrapping `set_bit_in__bitmap_and_heap`.

**UUID-mapped pools (from `DECLARE_API__UUID_MAPPED__POOL` macro — broken template, no in-repo users):**
- `static inline void initialize_{name}(name *);` — calls `initialize_serialization_pool`.
- `static inline type_value *allocate_{type_value}_from__{name}(name *);` — returns element pointer.
- `static inline void release_{type_value}_from__{name}(name *, type_value *);` — releases slot.
- `static inline type_value *dehash_p_{type_value}_from__{name}(name *, Identifier__u32);` — resolves UUID to element pointer via the undefined `DEHASH` macro.

**Enum map (from `DEFINE_API__ENUM_MAP` macro):**
- `static inline type_value *get_p_{type_value}_by__enum_key_from__{name}(name *, type_enum);` — bounds-checked (debug only) pointer to the entry.
- `void initialize_enum_map__{name}(name *);` — memset to zero.
- `void register_{type_value}_into__{name}(name *, type_enum, type_value);` — sets entry (bounds-checked in debug).
- `type_value get_{type_value}_from__{name}(name *, type_enum);` — returns `_values[type_enum__None]` on invalid key (debug only; release indexes unchecked).

## Key Files Table

| File | Role |
|------|------|
| `core/source/util/bitmap/bitmap.c` | Bitmap init, bitmap+heap set, heap-based first-set-bit search |
| `core/include/util/bitmap/bitmap.h` | `BITMAP`/`BITMAP_AND_HEAP` macros, inline get/set/clear, `SET_BIT_IN__BITMAP_AND_HEAP` |
| `core/include/util/hash_map/hash_map.h` | `UUID_MAPPED__POOL` struct macro; the generated API is a broken, unused template |
| `core/include/util/enum_map/enum_map.h` | `ENUM_MAP` struct macro, `DEFINE_API__ENUM_MAP` and `DECLARE_API__ENUM_MAP` API macros |
| `core/include/util/getter/getter.h` | Empty placeholder |
