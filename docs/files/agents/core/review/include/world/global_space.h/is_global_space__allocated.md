// Review:
// - File: core/include/world/global_space.h
// - Lines: 46 - 53
//   static inline
//   bool is_global_space__allocated(
//           Global_Space *p_global_space) {
//       return p_global_space
//           && !is_serialized_struct__deallocated__uuid_64(
//                   &p_global_space->_serialization_header)
//           && p_global_space->quantity_of__references;
//   }
