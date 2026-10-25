// Review:
// - File: core/source/world/global_space.c
// - Lines: 30 - 38
//   void initialize_global_space(
//           Global_Space *p_global_space) {
//       memset(p_global_space,
//               0,
//               sizeof(Global_Space));
//       initialize_serialization_header_for__deallocated_struct__uuid_64(
//               &p_global_space->_serialization_header, 
//               sizeof(Global_Space));
//   }
