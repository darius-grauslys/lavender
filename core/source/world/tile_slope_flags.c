#include "world/tile_slope_flags.h"
#include "defines.h"
#include "defines_weak.h"
#include "numerics.h"
#include "vectors.h"
#include "world/global_space_manager.h"
#include "world/world.h"

Tile_Slope_Flags__u4 get_tile_slope_flags(
        World *p_world,
        Tile_Vector__3i32 tile_vector__3i32,
        Direction__u8 direction_mask__u8) {
    tile_vector__3i32.z__i32++;
    Tile *p_tile__north = 
        get_p_tile_from__global_space_manager(
                get_p_global_space_manager_from__world(
                    p_world), 
                add_vectors__3i32(
                    tile_vector__3i32,
                    VECTOR__3i32__0_1_0));
    Tile *p_tile__east =
        get_p_tile_from__global_space_manager(
                get_p_global_space_manager_from__world(
                    p_world), 
                add_vectors__3i32(
                    tile_vector__3i32,
                    VECTOR__3i32__1_0_0));
    Tile *p_tile__south =
        get_p_tile_from__global_space_manager(
                get_p_global_space_manager_from__world(
                    p_world), 
                add_vectors__3i32(
                    tile_vector__3i32,
                    VECTOR__3i32__0_n1_0));
    Tile *p_tile__west =
        get_p_tile_from__global_space_manager(
                get_p_global_space_manager_from__world(
                    p_world), 
                add_vectors__3i32(
                    tile_vector__3i32,
                    VECTOR__3i32__n1_0_0));

    Tile_Slope_Flags__u4 tile_slope_flags = 0;
    if (p_tile__north
            && (direction_mask__u8 & DIRECTION__NORTH)
            && p_tile__north->the_kind_of__tile
            != Tile_Kind__None) {
        tile_slope_flags |=
            TILE_SLOPE_FLAG__NORTH;
    }
    if (p_tile__east
            && (direction_mask__u8 & DIRECTION__EAST)
            && p_tile__east->the_kind_of__tile
            != Tile_Kind__None) {
        tile_slope_flags |=
            TILE_SLOPE_FLAG__EAST;
    }
    if (p_tile__south
            && (direction_mask__u8 & DIRECTION__SOUTH)
            && p_tile__south->the_kind_of__tile
            != Tile_Kind__None) {
        tile_slope_flags |=
            TILE_SLOPE_FLAG__SOUTH;
    }
    if (p_tile__west
            && (direction_mask__u8 & DIRECTION__WEST)
            && p_tile__west->the_kind_of__tile
            != Tile_Kind__None) {
        tile_slope_flags |=
            TILE_SLOPE_FLAG__WEST;
    }

    if (!tile_slope_flags)
        return tile_slope_flags;
    switch (~tile_slope_flags) {
        default:
            return tile_slope_flags;
        case 0:
        case TILE_SLOPE_FLAG__NORTH:
        case TILE_SLOPE_FLAG__EAST:
        case TILE_SLOPE_FLAG__SOUTH:
        case TILE_SLOPE_FLAG__WEST:
            return 0;
    }
}

i32F4 get_z_offset_of__tile_slope_flags__i32F4(
        Tile_Slope_Flags__u4 tile_slope_flags,
        i32F4 x__i32F4,
        i32F4 y__i32F4) {
    i32F4 z_going__north__i32F4 = 0;
    i32F4 z_going__east__i32F4 = 0;
    i32F4 z_going__south__i32F4 = 0;
    i32F4 z_going__west__i32F4 = 0;

    if (is_tile_slope_flags__north(
                tile_slope_flags)) {
        z_going__north__i32F4 =
            MASK(FRACTIONAL_PERCISION_4__BIT_SIZE)
            & abs(y__i32F4);
    }
    if (is_tile_slope_flags__east(
                tile_slope_flags)) {
        z_going__east__i32F4 =
            MASK(FRACTIONAL_PERCISION_4__BIT_SIZE)
            & abs(x__i32F4);
    }
    if (is_tile_slope_flags__south(
                tile_slope_flags)) {
        z_going__south__i32F4 =
            MASK(FRACTIONAL_PERCISION_4__BIT_SIZE)
            - (MASK(FRACTIONAL_PERCISION_4__BIT_SIZE)
                & abs(y__i32F4));
    }
    if (is_tile_slope_flags__west(
                tile_slope_flags)) {
        z_going__west__i32F4 =
            MASK(FRACTIONAL_PERCISION_4__BIT_SIZE)
            - (MASK(FRACTIONAL_PERCISION_4__BIT_SIZE)
                & abs(x__i32F4));
    }

    return max__i32(
            z_going__north__i32F4,
            max__i32(
                z_going__east__i32F4,
                max__i32(
                    z_going__south__i32F4,
                    z_going__west__i32F4)));
}
