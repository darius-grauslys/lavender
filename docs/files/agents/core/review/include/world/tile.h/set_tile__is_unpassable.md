// Review:
// - File: core/include/world/tile.h
// - Lines: 14 - 18
//   static inline 
//   void set_tile__is_unpassable(Tile_Flags__u8 *p_tile_flags__u8, bool value) {
//       *p_tile_flags__u8 &= ~TILE_FLAGS__BIT_IS_UNPASSABLE;
//       *p_tile_flags__u8 |= (value << TILE_FLAGS__BIT_SHIFT_IS_UNPASSABLE);
//   }
