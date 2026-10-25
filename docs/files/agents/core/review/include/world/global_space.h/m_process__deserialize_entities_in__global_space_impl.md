// Review:
// - File: core/source/world/global_space.c
// - Lines: 123 - 151
//   void m_process__deserialize_entities_in__global_space(
//           Process *p_this_process,
//           Game *p_game) {
//       Serialization_Request *p_serialization_request =
//           (Serialization_Request*)p_this_process->p_process_data;
//       Global_Space *p_global_space = 
//           (Global_Space*)p_serialization_request->p_data;
//
//       Collision_Node *p_collision_node =
//           get_p_collision_node_from__global_space(
//                   p_global_space);
//
//       if (!p_serialization_request->quantity_of__file_contents--) {
//           complete_process(p_this_process);
//           return;
//       }
//
//       Entity *p_entity =
//           allocate_entity_in__entity_manager(
//                   p_game, 
//                   get_p_world_from__game(p_game),
//                   get_p_entity_manager_from__game(p_game),
//                   Entity_Kind__None);
//
//       deserialize_entity(
//               p_game, 
//               p_serialization_request,
//               p_entity);
//   }
