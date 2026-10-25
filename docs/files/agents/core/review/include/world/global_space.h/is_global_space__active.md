// Review:
// - File: core/include/world/global_space.h
// - Lines: 182 - 191
//   static inline
//   bool is_global_space__active(
//           Global_Space *p_global_space) {
//       return p_global_space
//           && !is_global_space__constructing(p_global_space)
//           && !is_global_space__awaiting_construction(p_global_space)
//           && !is_global_space__deconstructing(p_global_space)
//           && !is_global_space__awaiting_deconstruction(p_global_space)
//           ;
//   }
