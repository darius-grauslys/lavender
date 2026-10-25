// Review:
// - File: core/include/world/global_space.h
// - Lines: 121 - 129
//   static inline
//   bool set_global_space_as__NOT_constructing(
//           Global_Space *p_global_space) {
//       set_global_space_as__NOT_awaiting_construction(
//               p_global_space);
//       return p_global_space->global_space_flags__u8 &=
//           ~GLOBAL_SPACE_FLAG__IS_CONSTRUCTING
//           ;
//   }
