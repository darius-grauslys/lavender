// Review:
// - File: core/source/world/global_space.c
// - Lines: 53 - 121
//   void m_process__serialize_entities_in__global_space(
//           Process *p_this_process,
//           Game *p_game) {
//       Serialization_Request *p_serialization_request =
//           (Serialization_Request*)
//           p_this_process->p_process_data;
//       Global_Space *p_global_space =
//           p_serialization_request
//           ->p_data;
//       Collision_Node *p_collision_node =
//           get_p_collision_node_from__global_space(
//                   p_global_space);
//
//       Collision_Node_Entry *p_collision_node__entry =
//           p_collision_node->p_linked_list__collision_node_entries__tail;
//
//       for (;p_collision_node__entry;
//               p_collision_node__entry = 
//               p_collision_node__entry->p_previous_entry) {
//           Identifier__u32 uuid__u32 =
//               p_collision_node__entry
//               ->uuid_of__hitbox__u32
//               ;
//
//           Entity *p_entity =
//               get_p_entity_by__uuid_from__entity_manager(
//                       get_p_entity_manager_from__world(
//                           get_p_world_from__game(p_game)), 
//                       uuid__u32);
//
//           if (!p_entity) {
//               debug_error("m_process__serialize_entities_in__global_space, failed to locate entity in collision_node.");
//               return;
//           }
//
//           serialize_entity(
//                   p_game,
//                   p_serialization_request, 
//                   p_entity);
//
//           release_entity_from__entity_manager(
//                   p_game, 
//                   get_p_world_from__game(p_game), 
//                   get_p_entity_manager_from__game(p_game), 
//                   p_entity);
//       }
//
//       complete_process(p_this_process);
//   }
