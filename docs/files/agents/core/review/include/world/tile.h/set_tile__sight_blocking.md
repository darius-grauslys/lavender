// Review:
// - File: core/include/world/tile.h
// - Lines: 31 - 35
//   static inline 
//   void set_tile__sight_blocking(Tile_Flags__u8 *p_tile_flags__u8, bool value) {
//       *p_tile_flags__u8 &= ~TILE_FLAGS__BIT_IS_SIGHT_BLOCKING;
//       *p_tile_flags__u8 |= (value << TILE_FLAGS__BIT_SHIFT_IS_SIGHT_BLOCKING);
//   }
