# System Overview: Bitmap Utilities

## Purpose

The bitmap module provides compact, fixed-size boolean arrays for
bit-level storage and lookup. Two variants are offered: a flat bitmap
for simple set/get operations, and a heap-accelerated bitmap that
layers a hierarchical summary for efficient first-set-bit queries.

Bitmaps are used throughout the engine wherever per-element boolean
state must be tracked compactly — allocation status, serialization
state, collision presence, packet fragment tracking, and site presence.

## Architecture

### Data Structures

    Flat Bitmap (BITMAP macro):
    +-------+-------+-------+-------+-----+
    | byte0 | byte1 | byte2 | byte3 | ... |   N/8 bytes total
    +-------+-------+-------+-------+-----+
      bits    bits    bits    bits
      0..7    8..15   16..23  24..31

    Heap-Accelerated Bitmap (BITMAP_AND_HEAP macro):
    +===================================+
    | Base Bitmap: N/8 bytes            |  bit-level data
    +-----------------------------------+
    | Heap Level 1: N/64 bytes          |  each bit summarizes 8 base bits
    +-----------------------------------+
    | Heap Level 2: N/512 bytes         |  each bit summarizes 8 level-1 bits
    +-----------------------------------+
    | ...                               |  continues until level size = 0
    +===================================+

### Bit Indexing

All bit indices are zero-based. Bit `i` is stored in byte `i >> 3` at
bit position `i & 0x7` (i.e. `BIT(i & MASK(3))`).

### Heap Structure

The heap is a sequence of summary levels appended after the base bitmap
in the same contiguous `u8` array. Each level summarizes the level below
by a factor of 8:

| Level | Byte Count | Each Bit Represents |
|-------|-----------|---------------------|
| Base | N/8 | 1 data bit |
| 1 | N/64 | Whether any of 8 base-level bits are set |
| 2 | N/512 | Whether any of 8 level-1 bits are set |
| k | N/(8^(k+1)) | Whether any of 8 level-(k-1) bits are set |

Levels continue until the byte count reaches 0. The total array size
is computed by the `BITMAP_AND_HEAP` macro as:

    N/8 + N/64 + N/512 + N/4096 + ... (up to N/2^30)

## Lifecycle

### 1. Declaration

    // Flat bitmap of 256 bits
    BITMAP(my_bitmap, 256);

    // Heap-accelerated bitmap of 512 bits
    BITMAP_AND_HEAP(my_heap_bitmap, 512);

Both macros declare a `u8` array. `N` must be a multiple of 8.

### 2. Initialization

    initialize_bitmap(my_bitmap, false, 256);

Sets all bits to the given state (`false` = all 0s, `true` = all 1s).
The third parameter is the number of **bits**, not bytes.

**Important**: `initialize_bitmap` only zeroes/fills `N/8` bytes (the
base bitmap). For `BITMAP_AND_HEAP`, the heap levels must also be
cleared. Callers should ensure the entire containing struct is zeroed,
or manually clear the heap portion.

### 3. Set / Get Operations

    // Query
    bool is_set = is_bit_set_in__bitmap(
            my_bitmap, 256, index);

    // Flat bitmap set/clear
    set_bit_in__bitmap(
            my_bitmap, 256, index, true);

    // Heap-accelerated set/clear (propagates through heap)
    set_bit_in__bitmap_and_heap(
            my_heap_bitmap,
            p_end_of__heap,
            512,
            index,
            true);

    // Convenience macro (computes p_end_of__heap automatically)
    SET_BIT_IN__BITMAP_AND_HEAP(
            my_heap_bitmap, 512, index, true);

### 4. First-Set-Bit Query (Heap Only)

    Index__u32 first = get_index_of__first_set_bit_from__bitmap_and_heap(
            my_heap_bitmap, 512);

    if (first == INDEX__UNKNOWN__u32) {
        // No bits are set
    }

The query traverses the heap top-down, checking each level to narrow
down which group of 8 contains a set bit, achieving O(log₈ N) time.

## Heap Propagation

When `set_bit_in__bitmap_and_heap` is called:

1. The base bitmap bit at `index` is set or cleared.
2. The corresponding byte in heap level 1 is updated: each bit in a
   heap byte represents whether **any** bit is set in the corresponding
   group of 8 bits at the base level.
3. The corresponding byte in heap level 2 is updated based on the
   level-1 byte.
4. Propagation continues up through all heap levels.

This ensures the heap is always consistent with the base bitmap after
every modification.

## Usage in the Engine

| System | Bitmap Variant | Purpose |
|--------|---------------|---------|
| Region serialization | Flat | `bitmap_of__serialized_chunks` — tracks which chunks have been serialized |
| Region sites | Flat | `bitmap_of__sites` — tracks site presence per region |
| Collision Node Pool | Flat | Allocation tracking for collision node entries |
| TCP Delivery | Flat | `TCP_PAYLOAD_BITMAP` — tracks received packet fragments |

## Choosing Between Variants

| Scenario | Recommended Variant | Rationale |
|----------|-------------------|-----------|
| Small bitmaps (≤ 64 bits) | `BITMAP` | Linear scan is fast; heap overhead is wasteful |
| Large bitmaps, frequent first-set-bit queries | `BITMAP_AND_HEAP` | O(log₈ N) lookup via heap |
| Large bitmaps, only set/get operations | `BITMAP` | No need for heap if first-set-bit is not queried |

## Error Handling

| Condition | Debug Build | Release Build |
|-----------|------------|---------------|
| Out-of-bounds `is_bit_set_in__bitmap` | `debug_error`, returns `false` | Undefined behavior |
| Out-of-bounds `set_bit_in__bitmap` | `debug_error`, no-op | Undefined behavior |
| No bits set in `get_index_of__first_set_bit_from__bitmap_and_heap` | Returns `INDEX__UNKNOWN__u32` | Returns `INDEX__UNKNOWN__u32` |

## Preconditions and Postconditions

### Preconditions

- `initialize_bitmap`: `p_bitmap` must be non-null. `size_of__bitmap`
  must be a multiple of 8.
- `is_bit_set_in__bitmap` / `set_bit_in__bitmap`: `index_of__bit` must
  be less than `size_of__bitmap`.
- `set_bit_in__bitmap_and_heap`: `p_end_of__heap` must point to the
  last byte of the heap array. `index_of__bit` must be less than
  `size_of__bitmap_but_NOT__including_heap`.
- `SET_BIT_IN__BITMAP_AND_HEAP`: `bitmap` must be a statically-sized
  array, not a pointer (relies on `sizeof(bitmap)`).

### Postconditions

- After `initialize_bitmap(_, false, _)`: all bits are 0.
- After `initialize_bitmap(_, true, _)`: all bits are 1.
- After `set_bit_in__bitmap`: the specified bit is set or cleared;
  no other bits are modified.
- After `set_bit_in__bitmap_and_heap`: the specified bit is set or
  cleared, and all heap levels are consistent with the base bitmap.
