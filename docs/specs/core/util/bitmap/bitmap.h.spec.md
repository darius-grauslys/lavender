# 1 Specification: core/include/util/bitmap/bitmap.h

## 1.1 Overview

Provides fixed-size bitmap utilities and an optional heap-accelerated
bitmap structure for efficient bit-level storage and lookup. Bitmaps are
used throughout the engine for compact boolean arrays — tracking allocation
status, serialization state, collision presence, and similar per-element
flags.

The "bitmap and heap" variant layers a hierarchical summary (heap) on top
of the flat bitmap, enabling O(log N) lookup of the first set bit instead
of O(N) linear scanning.

## 1.2 Dependencies

- `debug/debug.h` (for `debug_error` in debug builds)
- `defines_weak.h` (for `u8`, `Quantity__u32`, `Index__u32`, `BIT`, `MASK`)

## 1.3 Types

### 1.3.1 Bitmap (macro-defined)

    #define BITMAP(name, N) \
        u8 name[ N >> 3 ]

Declares a flat bitmap of `N` bits as a `u8` array of `N / 8` bytes.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | identifier | The variable name for the bitmap array. |
| `N` | integer constant | Number of bits. Must be a multiple of 8. |

### 1.3.2 Bitmap and Heap (macro-defined)

    #define BITMAP_AND_HEAP(name, N) \
        u8 name[ (N >> 3) \
        + (N >> 6) \
        + (N >> 9) \
        + (N >> 12) \
        + (N >> 15) \
        + (N >> 18) \
        + (N >> 21) \
        + (N >> 24) \
        + (N >> 27) \
        + (N >> 30) ]

Declares a bitmap of `N` bits followed by a hierarchical heap summary.
Each successive heap level summarizes 8 entries from the level below into
a single byte (each bit represents whether any bit is set in the
corresponding group of 8). This enables fast first-set-bit queries.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | identifier | The variable name for the combined bitmap+heap array. |
| `N` | integer constant | Number of bits in the base bitmap. Must be a multiple of 8. |

**Memory layout** (for `N` bits):

    [ base bitmap: N/8 bytes ]
    [ heap level 1: N/64 bytes ]
    [ heap level 2: N/512 bytes ]
    [ ... ]
    (continues until level size reaches 0)

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_bitmap` | `(u8 *p_bitmap, bool state, Quantity__u32 size_of__bitmap) -> void` | Sets all bits in the bitmap to `state` (true = all 1s, false = all 0s). `size_of__bitmap` is the number of **bits**. |

### 1.4.2 Flat Bitmap Operations (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_bit_set_in__bitmap` | `(u8 *p_bitmap, Quantity__u32 size_of__bitmap, Index__u32 index_of__bit) -> bool` | `bool` | Returns `true` if the bit at `index_of__bit` is set. `size_of__bitmap` is in bits. Debug builds call `debug_error` on out-of-bounds access. |
| `set_bit_in__bitmap` | `(u8 *p_bitmap, Quantity__u32 size_of__bitmap, Index__u32 index_of__bit, bool state_of__bit) -> void` | `void` | Sets or clears the bit at `index_of__bit`. `size_of__bitmap` is in bits. Debug builds call `debug_error` on out-of-bounds access. |

### 1.4.3 Heap-Accelerated Bitmap Operations

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_index_of__first_set_bit_from__bitmap_and_heap` | `(u8 *p_bitmap_and_heap, Quantity__u32 size_of__bitmap_but_NOT__including_heap) -> Index__u32` | `Index__u32` | Returns the index of the first set bit in the bitmap, using the heap for acceleration. `size_of__bitmap_but_NOT__including_heap` is the number of **bits** in the base bitmap (not including heap bytes). Returns `INDEX__UNKNOWN__u32` if no bit is set. |
| `set_bit_in__bitmap_and_heap` | `(u8 *p_bitmap, u8 *p_end_of__heap, Quantity__u32 size_of__bitmap_but_NOT__including_heap, Index__u32 index_of__bit, bool state_of__bit) -> void` | `void` | Sets or clears a bit in the base bitmap and propagates the change up through all heap levels. `p_end_of__heap` points to the last byte of the heap. |

### 1.4.4 Heap-Accelerated Bitmap Convenience Macro

    #define SET_BIT_IN__BITMAP_AND_HEAP(
            bitmap,
            size_of__bitmap_but_NOT__including_heap,
            index,
            state)

Wraps `set_bit_in__bitmap_and_heap`, automatically computing `p_end_of__heap`
from `sizeof(bitmap)`. Only valid when `bitmap` is a statically-sized array
(not a pointer).

| Parameter | Type | Description |
|-----------|------|-------------|
| `bitmap` | array | The bitmap+heap array (must be a named array, not a pointer). |
| `size_of__bitmap_but_NOT__including_heap` | integer | Number of bits in the base bitmap. |
| `index` | `Index__u32` | Bit index to set or clear. |
| `state` | `bool` | `true` to set, `false` to clear. |

## 1.5 Agentic Workflow

### 1.5.1 When to Use Flat Bitmap vs Bitmap-and-Heap

| Scenario | Structure | Rationale |
|----------|-----------|-----------|
| Small bitmaps (≤ 64 bits) | `BITMAP` | Linear scan is fast enough; heap overhead is wasteful. |
| Large bitmaps with frequent first-set-bit queries | `BITMAP_AND_HEAP` | O(log N) first-set-bit lookup via heap. |
| Large bitmaps with only set/get operations | `BITMAP` | No need for heap if first-set-bit is not queried. |

### 1.5.2 Usage in the Engine

Bitmaps are used in several core systems:

- **Region serialization**: `Region.bitmap_of__serialized_chunks` tracks
  which chunks have been serialized.
- **Collision nodes**: `Collision_Node_Pool` uses bitmaps for allocation
  tracking.
- **TCP delivery**: `TCP_PAYLOAD_BITMAP` tracks received packet fragments.
- **Sites**: `Region.bitmap_of__sites` tracks site presence.

### 1.5.3 Initialization Pattern

    // Flat bitmap
    BITMAP(my_bitmap, 256);
    initialize_bitmap(my_bitmap, false, 256);

    // Bitmap with heap
    BITMAP_AND_HEAP(my_heap_bitmap, 512);
    initialize_bitmap(my_heap_bitmap, false, 512);

**Note**: `initialize_bitmap` only initializes the base bitmap bytes. For
`BITMAP_AND_HEAP`, the heap levels should also be zeroed. Since
`initialize_bitmap` uses `memset` on `size_of__bitmap / 8` bytes, the
caller should ensure the heap portion is also cleared (e.g. by zeroing
the entire containing struct).

### 1.5.4 Bit Indexing Convention

All bit indices are zero-based. Bit `i` is stored in byte `i >> 3` at
bit position `i & 0x7` (i.e. `BIT(i & MASK(3))`).

### 1.5.5 Heap Propagation

When using `set_bit_in__bitmap_and_heap`:

1. The base bitmap bit is set or cleared.
2. The corresponding heap level 1 byte is updated: each bit in a heap
   byte represents whether **any** bit is set in the corresponding group
   of 8 bits at the level below.
3. Propagation continues up through all heap levels.

This ensures `get_index_of__first_set_bit_from__bitmap_and_heap` can
traverse the heap top-down to find the first set bit in O(log₈ N) steps.

### 1.5.6 Preconditions

- `initialize_bitmap`: `p_bitmap` must be non-null. `size_of__bitmap`
  must be a multiple of 8.
- `is_bit_set_in__bitmap` / `set_bit_in__bitmap`: `index_of__bit` must
  be less than `size_of__bitmap`. Debug builds emit `debug_error` on
  out-of-bounds access and return early (false for queries, no-op for sets).
- `set_bit_in__bitmap_and_heap`: `p_end_of__heap` must point to the last
  byte of the heap array. `index_of__bit` must be less than
  `size_of__bitmap_but_NOT__including_heap`.
- `SET_BIT_IN__BITMAP_AND_HEAP`: `bitmap` must be a statically-sized
  array, not a pointer (relies on `sizeof(bitmap)`).

### 1.5.7 Postconditions

- After `initialize_bitmap` with `state = false`: all bits are 0.
- After `initialize_bitmap` with `state = true`: all bits are 1.
- After `set_bit_in__bitmap`: the specified bit is set or cleared;
  no other bits are modified.
- After `set_bit_in__bitmap_and_heap`: the specified bit is set or
  cleared, and all heap levels are consistent with the base bitmap.

### 1.5.8 Error Handling

- Out-of-bounds access in `is_bit_set_in__bitmap` returns `false` in
  debug builds and emits `debug_error`.
- Out-of-bounds access in `set_bit_in__bitmap` is a no-op in debug
  builds and emits `debug_error`.
- In release builds (`NDEBUG` defined), no bounds checking is performed;
  out-of-bounds access is undefined behavior.
