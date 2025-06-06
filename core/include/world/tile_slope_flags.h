#ifndef TILE_SLOPE_FLAGS_H
#define TILE_SLOPE_FLAGS_H

#include "defines.h"
#include "defines_weak.h"

///
/// Slope flags are determined on the following neighbors
/// having non-none tile_kinds:
/// (+/-1, +/-1, +1)
///
/// In otherwords, the above z layer, and directly adjacent.
///
/// Returns a flag set with no more than 2 flags set.
///
/// NOTE: If 3 or more neighbors are found, then a flags set
/// of all unset flags are returned.
///
Tile_Slope_Flags__u4 get_tile_slope_flags(
        World *p_world,
        Tile_Vector__3i32 tile_vector__3i32,
        Direction__u8 direction_mask__u8);

i32F4 get_z_offset_of__tile_slope_flags__i32F4(
        Tile_Slope_Flags__u4 tile_slope_flags,
        i32F4 x__i32F4,
        i32F4 y__i32F4);

static inline
i32F4 snap_z_to__offset_of__tile_slope_flags__i32F4(
        Tile_Slope_Flags__u4 tile_slope_flags,
        i32F4 x__i32F4,
        i32F4 y__i32F4,
        i32F4 z__i32F4) {
    return (z__i32F4
            & ~MASK(FRACTIONAL_PERCISION_4__BIT_SIZE))
        | get_z_offset_of__tile_slope_flags__i32F4(
                tile_slope_flags, 
                x__i32F4, 
                y__i32F4);
}

static inline
bool is_tile_slope_flags__north(
        Tile_Slope_Flags__u4 tile_slope_flags) {
    return tile_slope_flags
        & TILE_SLOPE_FLAG__NORTH;
}

static inline
bool is_tile_slope_flags__east(
        Tile_Slope_Flags__u4 tile_slope_flags) {
    return tile_slope_flags
        & TILE_SLOPE_FLAG__EAST;
}

static inline
bool is_tile_slope_flags__south(
        Tile_Slope_Flags__u4 tile_slope_flags) {
    return tile_slope_flags
        & TILE_SLOPE_FLAG__SOUTH;
}

static inline
bool is_tile_slope_flags__west(
        Tile_Slope_Flags__u4 tile_slope_flags) {
    return tile_slope_flags
        & TILE_SLOPE_FLAG__WEST;
}
#endif
