// Review:
// - File: core/include/world/global_space.h
// - Lines: 36 - 44
//   static inline
//   bool drop_global_space(
//           Global_Space *p_global_space) {
//       if (--p_global_space->quantity_of__references <= 1) {
//           p_global_space->quantity_of__references = 1;
//           return true;
//       }
//       return false;
//   }
