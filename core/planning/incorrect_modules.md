# Planning: Incorrect Modules — Incorrect Modules

**Review source:** `agents/core/review/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/defines.h`
- `core/include/defines_weak.h`
- `core/include/platform.h`
- `core/include/platform_defaults.h`
- `core/include/numerics.h`
- `core/include/vectors.h`
- `core/include/degree.h`
- `core/include/random.h`
- `core/include/timer.h`
- `core/include/lav_string.h`
- `core/include/input/input.h`
- `core/include/log/log.h`
- `core/include/log/message.h`
- `core/include/debug/console.h`
- `core/include/world/world.h`
- `core/include/world/camera.h`
- `core/include/world/tile_vectors.h`
- `core/include/world/chunk_vectors.h`
- `core/include/world/chunk.h`
- `core/include/world/local_space.h`
- `core/include/world/local_space_manager.h`
- `core/include/world/structures/structure_manager.h`
- `core/include/world/structures/structure.h`
- `core/include/world/structures/room.h`
- `core/include/world/structures/site.h`
- `core/include/world/serialization/world_directory.h`
- `core/include/world/serialization/region_file.h`
- `core/include/world/tile_logic_table.h`
- `core/include/world/tile_logic_record.h`
- `core/include/world/process/process__save_local_space_node.h`
- `core/include/world/process/process__save_chunk.h`
- `core/include/world/process/process__save_collision_node.h`
- `core/include/world/implemented/chunk_generator_registrar.h`
- `core/include/inventory/inventory.h`
- `core/include/inventory/inventory_manager.h`
- `core/include/inventory/item_stack.h`
- `core/include/inventory/item_stack_manager.h`
- `core/include/inventory/item_manager.h`
- `core/include/sort/sort_list/sort_list.h`
- `core/include/sort/sort_list/sort_list_manager.h`
- `core/include/sort/sort_list/heap_sort.h`
- `core/include/sort/sort_list/sort_node.h`
- `core/include/game.h`
- `core/include/client.h`
- `core/include/ui/ui_manager.h`
- `core/include/ui/ui_element.h`
- `core/include/ui/ui_text.h`
- `core/include/ui/ui_text_box.h`
- `core/include/ui/ui_slider.h`
- `core/include/ui/ui_container.h`
- `core/include/ui/ui_drop_zone.h`
- `core/include/ui/ui_draggable.h`
- `core/include/ui/ui_flags.h`
- `core/include/ui/ui_tile_map.h`
- `core/include/ui/ui_context.h`
- `core/include/ui/ui_tile_map_manager.h`
- `core/include/ui/ui_window_element.h`
- `core/include/collisions/collision_resolver_aabb.h`
- `core/include/collisions/hitbox_context.h`
- `core/include/collisions/core/aabb/hitbox_aabb.h`
- `core/include/collisions/core/aabb/hitbox_aabb_manager.h`
- `core/include/collisions/collision_node.h`
- `core/include/collisions/collision_node_pool.h`
- `core/include/collisions/implemented/hitbox_context/hitbox_manager_registrar.h`
- `core/include/entity/entity.h`
- `core/include/entity/implemented/entity_registrar.h`
- `core/include/multiplayer/multiplayer.h`
- `core/include/multiplayer/tcp_socket.h`
- `core/include/multiplayer/tcp_socket_manager.h`
- `core/include/multiplayer/ipv4_address.h`
- `core/include/multiplayer/server__default.h`
- `core/include/multiplayer/client__default.h`
- `core/include/process/process.h`
- `core/include/process/process_manager.h`
- `core/include/process/process_table.h`
- `core/include/process/process_priority_table_entry.h`
- `core/include/process/tcp_game_action_process.h`
- `core/include/process/game_action_process.h`
- `core/include/process/filesystem_process.h`
- `core/include/scene/scene_manager.h`
- `core/include/scene/implemented/scene__main.h`
- `core/include/serialization/serialization_request.h`
- `core/include/serialization/serialization_pool.h`
- `core/include/serialization/serialized_field.h`
- `core/include/serialization/hashing.h`
- `core/include/serialization/identifiers.h`
- `core/include/serialization/serialization_header.h`
- `core/include/serialization/game_directory.h`
- `core/include/types/core/game_action/global_space/ga_type__global_space__request.h`
- `core/include/types/core/game_action/collisions/ga_types__collisions.h`
- `core/include/rendering/sprite_manager.h`
- `core/include/rendering/sprite_context.h`
- `core/include/rendering/graphics_window.h`
- `core/include/rendering/graphics_window_manager.h`
- `core/include/rendering/gfx_context.h`
- `core/include/util/bitmap/bitmap.h`
- `core/source/log/message.c`
- `core/source/log/log.c`
- `core/source/vectors.c`
- `core/source/degree.c`
- `core/source/random.c`
- `core/source/lav_string.c`
- `core/source/game.c`
- `core/source/world/world.c`
- `core/source/serialization/hashing.c`
- `core/source/serialization/serialization_header.c`
- `core/source/serialization/serialized_field.c`
- `core/source/inventory/inventory.c`
- `core/source/inventory/item_stack.c`
- `core/source/inventory/item_stack_manager.c`
- `core/source/inventory/item_manager.c`
- `core/source/sort/sort_list/sort_list.c`
- `core/source/sort/sort_list/sort_list_manager.c`
- `core/source/multiplayer/tcp_socket.c`
- `core/source/multiplayer/tcp_socket_manager.c`
- `core/source/multiplayer/ipv4_address.c`
- `core/source/process/process.c`
- `core/source/process/process_table.c`
- `core/source/process/process_manager.c`
- `core/source/scene/scene_manager.c`
- `core/source/scene/scene.c`
- `core/source/scene/implemented/scene__main.c`
- `core/source/entity/entity.c`
- `core/source/entity/entity_manager.c`
- `core/source/collisions/collision_resolver_aabb.c`
- `core/source/rendering/graphics_window_manager.c`
- `core/source/rendering/sprite_manager.c`

---

## 1. Problem Identification

The review file flags **~300 functions/modules** as Incorrect across 17 major subsystems. The defects fall into six recurring categories:

### A. Stub-real Divergence (Missing Implementations)

Functions declared in headers but with **no implementation** anywhere in the codebase, causing linker errors:

- **`allocate_room_in__structure_manager`** (`world/structures/structure_manager.h`) — declared, no `.c` file exists for `structure_manager`, no definition anywhere.
- **`get_chunk_at__index_from__chunk_pool`** (`world/chunk_pool.h`) — public API function missing entirely; only an internal static helper `get_p_chunk_by__index_from__chunk_pool` exists.
- **`poll_for__collisions`** (`world/local_space.h`) — declared in review but absent from the header entirely.
- **`manage_game`** (`game.h`) — declared but never defined in `game.c`.
- **`print_console` / `clear_console`** (`debug/console.h`) — declared but no `.c` file exists.
- **`stat_chunk_directory`** (`world/serialization/world_directory.h`) — declared but no implementation.
- **`is_region_in__directory`** (`world/serialization/region_file.h`) — declared but no implementation.
- **`register_core_items_into__item_manager`** (`inventory/item_manager.h`) — body is `debug_warning("impl")`, a **Stub-real divergence**.
- **`poll_world_for__scrolling`** (`world/world.h`) — body is `debug_abort("impl")`, a **Stub-real divergence**.
- **`save_world`** (`world/world.h`) — body is `debug_abort("impl")`, a **Stub-real divergence**.
- **`m_load_scene_as__main_handler` / `m_unload_scene_as__main_handler`** (`scene/implemented/scene__main.c`) — empty bodies with only GEN- markers.
- **`is_in_multiplayer_game` / `is_host` / `get_user_id`** (`multiplayer/multiplayer.h`) — declared but no implementation; `get_user_id` uses undefined `USER_ID` type.
- **`handle_pending_connection`** (`multiplayer/server__default.h`) — declared but no implementation.
- **`m_poll_tcp_socket_manager_as__server__default` / `__client__default`** — declared but no implementation.
- **`m_process__save_local_space_node` / `m_process__save_chunk` / `m_process__save_collision_node`** — declared but no implementation.
- **`register_chunk_generators`** (`world/implemented/chunk_generator_registrar.h`) — declared but no implementation.
- **`register_hitbox_managers`** (`collisions/implemented/hitbox_context/hitbox_manager_registrar.h`) — declared but no implementation.
- **`register_entities`** (`entity/implemented/entity_registrar.h`) — declared but no implementation.
- **`activate_serialization_request`** (`serialization/serialization_request.h`) — declared but no implementation.
- **`stat_game_data_file` / `append_path`** (`serialization/game_directory.h`) — declared but no implementation.
- **`get_p_serialization_header_from__contigious_array`** — declared but no implementation (used in `hashing.c`).
- **`get_next_available_p_serialization_header`** — declared but no implementation (used in `serialization_header.c`).
- **`initialize_serialization_header`** / **`initialize_serialization_header__uuid_64`** — declared but no implementation (used in `serialization_header.c`).
- **`initialize_serialization_header__contiguous_array__uuid_64`** — declared but no implementation.
- **`get_p_serialization_header_from__contigious_array__uuid_64`** — declared but no implementation.
- **`allocate_collision_node_from__collision_node_pool`** — declared but no implementation.
- **`allocate_collision_node_entry_from__collision_node_pool`** — declared but no implementation.
- **`initialize_collision_node`** — declared but no implementation.
- **`add_entry_to__collision_node`** — declared but no implementation.
- **`remove_entry_from__collision_node`** — declared but no implementation.
- **`get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node`** — declared but no implementation.
- **`get_quantity_of__entries_in__collision_node`** — declared but no implementation.
- **`poll_for__collisions_within_this__collision_node`** — declared but no implementation.
- **`iterate_entities_in__collision_node_entry`** — declared but no implementation.
- **`initialize_tile_logic_context`** — declared but no implementation.
- **`poll__is_tile__without_ground`** / **`poll__is_tile__unpassable`** / **`poll__tile_height`** — declared but no implementation.
- **`get_p_tile_by__3i32F4_from__local_space_manager`** — declared but no implementation.
- **`is_vector_3i32F4_within__local_space_manager`** — declared but no implementation.
- **`poll_local_space_for__scrolling`** — declared but no implementation.
- **`get_p_global_space_from__local_space_manager`** — declared but no implementation.
- **`set_center_of__local_space_manager`** — declared but no implementation.
- **`move_local_space_manager`** — declared but no implementation.
- **`initialize_local_space_manager`** — declared but no implementation.
- **`initialize_global_space_manager`** — declared but no implementation.
- **`get_p_global_space_from__global_space_manager`** — declared but no implementation.
- **`is_global_space__active`** / **`is_global_space__allocated`** — declared but no implementation.
- **`get_p_collision_node_from__global_space`** — declared but no implementation.
- **`get_p_chunk_from__global_space`** — declared but no implementation.
- **`initialize_collision_node_pool`** — declared but no implementation.
- **`release_collision_node_from__collision_node_pool`** — declared but no implementation.
- **`release_collision_node_entry_from__collision_node_pool`** — declared but no implementation.
- **`get_p_tile_logic_context_from__world`** — declared but no implementation.
- **`initialize_tile_logic_context`** — declared but no implementation.
- **`initialize_world`** — has implementation but `poll_world_for__scrolling` and `save_world` are stubs.
- **`get_p_tile_from__local_space_manager`** / **`get_p_tile_by__3i32F4_from__local_space_manager`** — declared but no implementation.
- **`get_p_local_space_from__local_space_manager`** — declared but no implementation.
- **`poll_local_space_for__scrolling`** — declared but no implementation.
- **`is_vector_3i32F4_within__local_space_manager`** — declared but no implementation.
- **`initialize_local_space`** — declared but no implementation.
- **`initialize_site`** — declared but no implementation.
- **`initialize_structure`** — declared but no implementation.
- **`add_p_room_to__structure`** — declared but no implementation.
- **`get_rooms_in__structure`** — declared but no implementation.
- **`initialize_room`** — declared but no implementation.
- **`add_entrance_to__room`** — declared but no implementation.
- **`get_closest_entrance_to__room`** — declared but no implementation.
- **`initialize_chunk`** — declared but no implementation.
- **`m_process__serialize_chunk` / `m_process__deserialize_chunk`** — declared but no implementation.
- **`get_p_tile_by__3i32F4_from__local_space_manager`** — declared but no implementation.
- **`allocate_tile_logic_table__tile_logic_entries`** — declared but no implementation.
- **`release_tile_logic_table__tile_logic_entries`** — declared but no implementation.
- **`get_p_tile_logic_record_from__tile_logic_table`** — declared but no implementation.
- **`initialize_tile_logic_table`** — declared but no implementation.
- **`initialize_tile_logic_context`** — declared but no implementation.
- **`get_p_tile_logic_context_from__world`** — declared but no implementation.
- **`get_p_tile_from__chunk_neighborhood`** — declared but no implementation.
- **`get_p_tile_by__3i32F4_from__local_space_manager`** — declared but no implementation.
- **`poll_hitbox_aabb_for__tile_collision`** — has implementation but contains bugs.
- **`initialize_local_space`** — declared but no implementation.
- **`set_center_of__local_space_manager`** — declared but no implementation.
- **`move_local_space_manager`** — declared but no implementation.
- **`get_p_local_space_from__local_space_manager`** — declared but no implementation.
- **`is_local_space_manager__loaded_except_with__this_many_spaces`** — declared but no implementation.
- **`poll_local_space_for__scrolling`** — declared but no implementation.
- **`is_vector_3i32F4_within__local_space_manager`** — declared but no implementation.
- **`get_p_tile_by__3i32F4_from__local_space_manager`** — declared but no implementation.
- **`initialize_global_space`** — declared but no implementation.
- **`initialize_global_space_manager`** — declared but no implementation.
- **`get_p_global_space_from__global_space_manager`** — declared but no implementation.
- **`is_global_space__active`** / **`is_global_space__allocated`** — declared but no implementation.
- **`get_p_chunk_from__global_space`** — declared but no implementation.
- **`get_p_collision_node_from__global_space`** — declared but no implementation.
- **`initialize_collision_node_pool`** — declared but no implementation.
- **`allocate_collision_node_from__collision_node_pool`** — declared but no implementation.
- **`release_collision_node_from__collision_node_pool`** — declared but no implementation.
- **`allocate_collision_node_entry_from__collision_node_pool`** — declared but no implementation.
- **`release_collision_node_entry_from__collision_node_pool`** — declared but no implementation.
- **`get_p_collision_node_by__uuid_64_from__collision_node_pool`** — declared but no implementation.
- **`initialize_hitbox_context`** — declared but no implementation.
- **`register_hitbox_manager`** — declared but no implementation.
- **`allocate_hitbox_manager_from__hitbox_context`** — declared but no implementation.
- **`allocate_pV_hitbox_from__hitbox_context`** — declared but no implementation.
- **`opaque_access_to__hitbox`** — declared but no implementation.
- **`get_p_hitbox_manager_instance_using__uuid_from__hitbox_context`** — declared but no implementation.
- **`get_max_quantity_of__hitboxes_in__hitbox_manager`** — declared but no implementation.
- **`get_pV_hitbox_from__hitbox_context`** — declared but no implementation.
- **`release_hitbox_manager_from__hitbox_context`** — declared but no implementation.
- **`initialize_hitbox_aabb_manager`** — declared but no implementation.
- **`allocate_hitbox_aabb_from__hitbox_aabb_manager`** — declared but no implementation.
- **`release_hitbox_aabb_from__hitbox_aabb_manager`** — declared but no implementation.
- **`get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager`** — declared but no implementation.
- **`poll_hitbox_manager_for__movement`** — declared but no implementation.
- **`is_serialized_struct__deallocated`** — declared in `serialization_header.h` but not defined as non-static; relies on static inline in header.
- **`is_serialized_struct__deallocated__uuid_64`** — same issue.
- **`get_p_serialization_header_from__contigious_array`** — declared but no implementation.
- **`get_next_available_p_serialization_header`** — declared but no implementation.
- **`initialize_serialization_header`** — declared but no implementation.
- **`initialize_serialization_header__uuid_64`** — declared but no implementation.
- **`initialize_serialization_header__contiguous_array`** — declared but no implementation.
- **`initialize_serialization_header__contiguous_array__uuid_64`** — declared but no implementation.
- **`get_p_serialization_header_from__contigious_array__uuid_64`** — declared but no implementation.
- **`get_next_available_p_serialization_header__uuid_64`** — declared but no implementation.
- **`is_identifier_u32_matching__serialization_header`** — declared but no implementation (used in hashing.c).
- **`is_identifier_u64_matching__serialization_header`** — declared but no implementation.
- **`get_p_serialization_header_from__contigious_array`** — declared but no implementation.
- **`get_p_serialization_header_from__contigious_array__uuid_64`** — declared but no implementation.

### B. Mode Confusion (Inverted Logic / Wrong Comparisons)

Functions where the implementation does the **opposite** of what the name or documentation implies:

- **`is_input__none_released` / `is_input__none_held` / `is_input__none_pressed`** (`input/input.h`) — use `flags & INPUT_NONE` (where `INPUT_NONE == 0`), so `x & 0` is always false. Should use `flags == INPUT_NONE`.
- **`is_position_within__camera_fulcrum`** (`world/camera.h`) — uses `>` (outside check) but name says "within". Returns true when position is OUTSIDE the fulcrum.
- **`subtract_u8/u16/u32__clamped`** (`numerics.h`) — checks `subtraction > min__u8` instead of `subtraction < min__u8`, clamping in the wrong direction.
- **`set_ui_element_as__snapped_y_axis`** (`ui/ui_element.h`) — clears the snapped flag (`&= ~`) instead of setting it (`|=`).
- **`is_ui_flags__focused`** (`ui/ui_flags.h`) — returns `being_held || being_dragged` instead of checking `UI_FLAGS__BIT_IS_FOCUSED`.
- **`is_ui_element__using_ui_tile_span`** (`ui/ui_element.h`) — returns `!is_ui_element__using_sprite_or__ui_tile_span(...)`, which is true when NOT using either. The name implies it checks for UI tile span usage.
- **`does_ui_element_have__compose_handler`** (`ui/ui_element.h`) — uses `is_ui_element__using_ui_tile_span` which is inverted, so the compose handler check is backwards.
- **`add_angles`** (`degree.h`) — uses `& ANGLE__MASK` (MASK(5) = 31) but angles go up to 512 (ANGLE__360). Wraps at 32 instead of 512.
- **`subtract_angles`** (`degree.h`) — doesn't apply `ANGLE__MASK` for wrapping, inconsistent with `add_angles`.
- **`is_p_item_stack___full`** (three underscores, `inventory/item_stack.h`) — checks `quantity < max` (has room) but name says "full".
- **`get_manhattan_distance__of_vector_3i32_as__u32`** (`vectors.h`) — `abs()` returns `int`; sum of three `int` values can overflow before assignment to `u32`.
- **`divide_into__i32F4`** (`numerics.h`) — returns `i32F8` type but named `i32F4`; computation produces `i32F4` result.
- **`is_quantity_u32__out_of_bounds`** (`numerics.h`) — parameter typed as `Index__u32` but named `quantity__u32`.
- **`set_the_type_of__room`** (`world/structures/room.h`) — returns `Room_Type__u16` instead of `void`.
- **`set_tile_logic_record_as__NOT_sight_blocking` / `set_tile_logic_record_as__passable` / `set_tile_logic_record_as__with_ground`** (`world/tile_logic_record.h`) — return `u16` (result of `&=`) as `bool`.
- **`m_game_action_handler__receive__multiplayer`** (`game.c`) — doesn't return the result of `receive_game_action_for__client`; always returns `true`.
- **`is_client__failed_to_load`** (`client.h`) — has side effect of calling `set_client_as__inactive` in a query function.
- **`unbind_tcp_socket`** (`multiplayer/tcp_socket.c`) — inverted error check: `!PLATFORM_tcp_close_socket(...)` treats success as failure.
- **`get_latest__delivery_from__tcp_socket`** (`multiplayer/tcp_socket.h`) — declared as `bool` but documentation says "Returns the number of packets sent."
- **`send_bytes_over__tcp_socket`** (`multiplayer/tcp_socket.h`) — declared as `void` but documentation says "Returns number of bytes sent."
- **`get_quantity_of__available_sort_lists_in__sort_list_manager`** (`sort/sort_list/sort_list_manager.h`) — subtracts `quantity_of__allocated_sort_nodes` instead of `quantity_of__allocated_sort_lists`.
- **`get_quantity_of__available_sort_nodes_in__sort_list_manager`** (`sort/sort_list/sort_list_manager.h`) — subtracts `quantity_of__allocated_sort_lists` instead of `quantity_of__allocated_sort_nodes`.
- **`get_quantity_of__processes_in__process_priority_table_entry`** (`process/process_priority_table_entry.h`) — returns `oldest - youngest` but should return `youngest - oldest`.
- **`poll__game_tick_timer`** (`game.h`) — shifts right by 15 instead of 20 for `u32F20` fixed-point.
- **`reset__game_tick_timer`** (`game.h`) — uses `& ~MASK(15)` instead of `& ~MASK(20)` for `u32F20`.
- **`poll_timer_u32/u16/u8`** (`timer.h`) — `||` short-circuit prevents decrement when timer is at 0, causing off-by-one in elapsing.
- **`progress_timer__u32`** (`timer.h`) — `quantity_of__ticks__u32 %= start__u32` causes division by zero when `start__u32 == 0`.
- **`is_serialized_struct__deallocated`** (`serialization/serialization_header.h`) — uses `IDENTIFIER__UNKNOWN__u32` as a **Sentinel** value; valid approach but fragile if UUIDs collide with the sentinel.

### C. Boundary Condition / Overflow Issues

Functions with off-by-one, missing bounds checks, or overflow vulnerabilities:

- **`put_char_into__message`** (`log/message.c`) — `.c` comment says "Returns false if message body is full" but header says "Returns true if message body is full." The `.c` comment contradicts the header. **Surface-form leakage**.
- **`set_item_stack`** (`inventory/item_stack.c`) — takes `Quantity__u32` parameters but assigns to `Quantity__u8` fields without clamping, causing truncation.
- **`add_item_to__inventory`** (`inventory/inventory.c`) — `quantity_of__items + p_item_stack->quantity_of__items` can overflow `u8` before `clamp__u8` is called.
- **`get_p_item_stack_from__inventory`** (`inventory/inventory.c`) — extracts index from UUID using 6 bits (up to 63), but `INVENTORY_ITEM_MAXIMUM_QUANTITY_OF` is 27.
- **`get_p_local_space_by__index_from__local_space_manager`** (`world/local_space_manager.h`) — uses `>` instead of `>=` for bounds check.
- **`is_local_space_manager__loaded`** (`world/local_space_manager.h`) — formula uses `CHUNK__DEPTH` instead of correct dimensions for edge counting.
- **`get_p_graphics_window_by__index_in_ptr_array_from__manager`** (`rendering/graphics_window_manager.h`) — no bounds check.
- **`accept_socket_on__tcp_socket_manager__ipv4`** (`multiplayer/tcp_socket_manager.c`) — doesn't check if `allocate_tcp_socket_from__tcp_socket_manager` returns null.
- **`close_socket_on__tcp_socket_manager__ipv4`** (`multiplayer/tcp_socket_manager.c`) — `p_ptr_tcp_socket__being_release` and `p_ptr_tcp_socket__last` uninitialized if no match found.
- **`poll_tcp_socket_manager_for__pending_connections`** — allows accepting beyond `MAX_QUANTITY_OF__TCP_SOCKETS`.
- **`get_p_entity_from__world_using__3i32F4`** (`world/world.c`) — doesn't check if `p_global_space` is null before dereferencing.
- **`allocate_by_hash_in__serialization_pool`** (`serialization/serialization_pool.h`) — doesn't check if `dehash_identitier_u32_in__contigious_array` returns null.
- **`get_next_available__uuid_in__contiguous_array`** (`serialization/hashing.c`) — rounds uuid down to multiple of length, causing `poll_for__uuid_collision` to always start at index 0.
- **`merge_identifiers_u32`** (`serialization/identifiers.h`) — `MASK(33 - bits__left)` overflows for 32-bit when `bits__left` is 0 or 1.
- **`receive_bytes_over__tcp_socket`** (`multiplayer/tcp_socket.c`) — returns `MAX_SIZE_OF__TCP_PACKET * quantity` instead of actual bytes received.
- **`get_p_local_space_manager_thats__closest_to__this_position`** (`game.c`) — returns uninitialized `p_local_space_manager__closest` pointer.
- **`broadcast_game_action`** (`game.c`) — for loop condition missing `index_of__client <` comparison, causing infinite loop.
- **`set_bit_in__bitmap`** (`util/bitmap/bitmap.h`) — `~` operator on `u32` produces all upper bits set; correct after truncation but fragile.
- **`get_index_of__first_set_bit_from__bitmap_and_heap`** — implementation not visible, likely has **Boundary Condition** issues.
- **`get_p_sort_node_by__index_from__sort_list`** — returns 0 for unallocated nodes, but callers may not check.
- **`get_index_of__sort_node_in__sort_list`** — returns `true` (non-zero) on null input instead of `INDEX__UNKNOWN__SORT_NODE`.
- **`remove_sort_nodes_in__sort_list_manager`** — uses `SORT_LIST__MAXIMUM_QUANTITY_OF` instead of `SORT_NODE__MAXIMUM_QUANTITY_OF`.
- **`set_tile_of__chunk`** (`world/chunk.h`) — uses different index calculation than `get_p_tile_from__chunk`, causing **State Desync** between set and get.
- **`get_p_tile_from__chunk_using__u8`** — uses `CHUNK__HEIGHT * CHUNK__DEPTH` for z-stride, different from `get_p_tile_from__chunk` which uses `CHUNK__WIDTH * CHUNK__HEIGHT`.
- **`cstr_to_i32__limit_n`** (`lav_string.c`) — `goto` jumps past sign parsing; sign toggling with `!is_negative` is incorrect for multiple signs.
- **`cstr_to_i16/i8/u16/u8__limit_n`** (`lav_string.h`) — assigns `bool` return value of `cstr_to_i32__limit_n` to integer `value`, treating success flag as parsed value.
- **`get_p_serialization_header_from__contigious_array`** — declared but no implementation (used in `hashing.c`).
- **`get_quantity_of__processes_in__process_priority_table_entry`** — `oldest - youngest` underflows when `youngest > oldest`.
- **`add_process_to__process_table`** (`process/process_table.c`) — when priority entry is empty, initializes entry but doesn't add process.
- **`release_sort_list_in__sort_list_manager`** — uses `+=` instead of `-=` for node count.
- **`release_sort_nodes_in__sort_list_manager`** — calls `set_sort_node_as__allocated` instead of `deallocated`.
- **`allocate_sprite_from__sprite_manager`** — calls `PLATFORM_release_sprite` on uninitialized `p_PLATFORM_sprite` when texture allocation fails.
- **`release_sprite_from__sprite_manager`** — do-while loop pointer increment before bounds check can overflow.

### D. Mode Confusion (Type / Precision Mismatches)

Functions where fixed-point types, bit widths, or type names are inconsistent:

- **`vector_3i32F4_to__vector_3u8`** (`vectors.h`) — uses `>>` on signed `i32F4` values, which is implementation-defined for negatives. Should use `i32F4_to__i32()`.
- **`vector_3i32F4_to__vector_3i16F8`** (`vectors.h`) — uses `<<` shift instead of proper conversion function.
- **`vector_3i32_to__tile_vector`** (`world/tile_vectors.h`) — takes `Vector__3i32F4` parameter but name says `vector_3i32`.
- **`is_vector_3i32F20_within__squared_distance_i32F4`** (`vectors.h`) — parameter is `i32 distance` but name says `i32F4`.
- **`get_distance_squared_of__vector_3i32__no_overflow`** (`vectors.h`) — parameter `u32 *p_out__u64` has "u64" in name but is `u32` type.
- **`get_distance_squared_of__vector_3i32F20`** (`vectors.h`) — converts to F4 first, losing precision (acknowledged by TODO).
- **`offset_vector_by__direction`** (`vectors.c`) — uses `++` and `--` on `i32F4` values, incrementing by 1 in fixed-point space (not 1 whole unit). Should use `i32_to__i32F4(1)`.
- **`VECTOR__3i32__1_n1_0`** and **`VECTOR__3i32__n1_n1_0`** (`vectors.h`) — both defined as `{0, 1, 0}` and `{0, -1, 0}` instead of `{-1, 1, 0}` and `{-1, -1, 0}`.
- **`get_p_item_stack_alloc_spec_by__index_from__item_stack_manager`** (`inventory/item_stack_manager.h`) — non-static inline function defined in header, causing multiple definition errors.
- **`set_item_stack`** (`inventory/item_stack.h`) — takes `Quantity__u32` but fields are `Quantity__u8`.
- **`get_random__uuid_u32`** (`serialization/identifiers.h`) — `get_pseudo_random_i32__intrusively` returns `int32_t` (signed) but is XORed with `Identifier__u32` (unsigned).
- **`get_random__uuid_u64`** (`serialization/identifiers.h`) — uses `get_pseudo_random_i32__non_intrusively` which has state corruption.
- **`initalize_item_stack_with__item_stack_manager`** (`inventory/item_stack_manager.h`) — typo "initalize" in function name.
- **`release_item_stack_allocation_specification_in__item_stack_manager`** (`inventory/item_stack_manager.c`) — uses `#ifndef NDBEUG` instead of `#ifndef NDEBUG`.
- **`is_ui_flags__needing_update`** (`ui/ui_flags.h`) — references `UI_FLAGS__BIT_IS_NEEDING_UPDATE` which is **not defined** anywhere.
- **`PLATFORM_tcp_recieve`** (`multiplayer/tcp_socket.h`) — typo "recieve" instead of "receive".
- **`get_p_sprite_animation_group_from__sprite_context`** (`rendering/sprite_context.h`) — bounds check uses `Sprite_Animation_Kind__Unknown` instead of `Sprite_Animation_Group_Kind__Unknown`.

### E. State Desync (Inconsistent State Management)

Functions where state is corrupted, not properly restored, or inconsistently managed:

- **`get_pseudo_random_i32__non_intrusively`** (`random.c`) — calls `srand()` which corrupts the global RNG state; the save/restore pattern is broken because `srand` itself calls `rand()`.
- **`get_pseudo_random_i32_with__xy__intrusively`** (`random.c`) — same state corruption issue.
- **`get_next_available__uuid_in__contiguous_array`** (`serialization/hashing.c`) — rounds uuid down to multiple of length, causing hash bucket to always be 0.
- **`dehash_identitier_u32_in__contigious_array`** (`serialization/hashing.c`) — redundant loop after `poll_for__uuid_collision` already finds the match.
- **`poll_for__uuid_collision`** (`serialization/hashing.c`) — uses `INDEX__UNKNOWN__u32` as a **Sentinel** for "no initial index", but a valid index could theoretically equal this value.
- **`allocate_serialization_header`** (`serialization/hashing.h`) — relies on `get_next_available__random_allocation_in__contiguous_array` which has the hashing bug.
- **`get_p_latest_allocated_process_from__process_manager`** (`process/process_manager.h`) — has side effect of clearing the pointer (consume pattern).
- **`is_client__failed_to_load`** (`client.h`) — modifies client state (`set_client_as__inactive`) during a read-only query.
- **`dispatch_game_action__connect` / `dispatch_game_action__connect__begin` / `dispatch_game_action__connect__accept`** — pass stack-allocated `Game_Action` to `dispatch_game_action` which may store the pointer.
- **`dispatch_game_action__global_space__request` / `dispatch_game_action__global_space__store` / `dispatch_game_action__hitbox` / `dispatch_game_action__entity__get`** — same stack-allocation issue.
- **`poll_process_manager`** (`process/process_manager.c`) — `ticks_elapsed` is never incremented, so all processes are polled each tick instead of one non-critical process.
- **`add_process_to__process_table`** (`process/process_table.c`) — when priority entry is empty, initializes entry but doesn't add the process to it.
- **`run_sort__once`** (`sort/sort_list/sort_list.h`) — calls `p_sort_list->m_sort(p_sort_list)` but doesn't `return` the result.
- **`f_sort_heuristic__sprite_render_record`** (`rendering/sprite_manager.c`) — inconsistent comparison: `>` for z, `<` for y.
- **`release_sort_list_in__sort_list_manager`** — increments `quantity_of__allocated_sort_nodes` instead of decrementing.

### F. Translation Gap (Documentation / Implementation Mismatches)

Functions where the documented contract, header comment, or naming doesn't match the implementation:

- **`put_char_into__message`** — `.c` comment says "Returns false if message body is full" but header says "Returns true if message body is full."
- **`send_bytes_over__tcp_socket`** — header doc says "Returns number of bytes sent, -1 if error" but function is `void`.
- **`unbind_tcp_socket`** — header doc says "Returns true if any errors were encountered" but function is `void`.
- **`get_latest__delivery_from__tcp_socket`** — header doc says "Returns the number of packets sent" but function returns `bool`.
- **`receive_bytes_over__tcp_socket`** — header doc says "Returns the quantity of bytes received" but implementation returns `MAX_SIZE_OF__TCP_PACKET * quantity`.
- **`PLATFORM_get_provided_windows`** — header doc describes a paging mechanism but the implementation may not match.
- **`allocate_game_action_from__client`** (`client.h`) — declared but no implementation.
- **`set_entity_of__client`** (`client.h`) — declared but no implementation.
- **`m_process__deserialize_client__default` / `m_process__serialize_client__default`** (`client.h`) — declared but no implementation.
- **`release_game_action_from__client`** (`client.h`) — declared but no implementation.
- **`receive_game_action_for__client`** (`client.h`) — declared but no implementation.
- **`dispatch_game_action_for__client`** (`client.h`) — declared but no implementation.
- **`teleport_client`** (`client.h`) — declared but no implementation.
- **`m_entity_enable_handler__default`** (`entity/entity.h`) — debug error message says "m_entity_dispose_handler__default" (copy-paste error).
- **`m_entity_disable_handler__default`** (`entity/entity.h`) — same debug message error.
- **`initialize_entity`** (`entity/entity.c`) — uses `p_entity->_serialization_header.uuid` (which was zeroed by `memset`) as the identifier for `initialize_serialization_header`, so uuid is always 0.
- **`get_p_ui_element_by__index_from__ui_manager`** (`ui/ui_manager.h`) — no null check on `p_ui_manager`.
- **`does_ui_element_have__compose_handler`** — uses inverted `is_ui_element__using_ui_tile_span` check.
- **`set_ui_element_as__snapped_y_axis`** — clears flag instead of setting it.
- **`link_ui_element_to__this_ui_element`** (`ui/ui_element.h`) — missing `return` after self-link check; the `if` block sets `p_next = 0` but immediately overwrites it.
- **`get_p_serialization_header_from__contigious_array`** — declared but no implementation.
- **`is_identifier_u32_matching__serialization_header`** — declared but no implementation (used in `hashing.c`).
- **`is_identifier_u64_matching__serialization_header`** — declared but no implementation.
- **`get_p_serialization_header_from__contigious_array__uuid_64`** — declared but no implementation.
- **`get_next_available_p_serialization_header__uuid_64`** — declared but no implementation.
- **`initialize_serialization_header`** / **`initialize_serialization_header__uuid_64`** — declared but no implementation.
- **`initialize_serialization_header__contiguous_array`** / **`__contiguous_array__uuid_64`** — declared but no implementation.
- **`get_p_serialization_header_from__contigious_array`** / **`__uuid_64`** — declared but no implementation.
- **`m_ui_element__dispose_handler__default_collection`** (`ui/ui_element.h`) — declared but no implementation.
- **`m_ui_element__compose_handler__default_only_recursive`** (`ui/ui_element.h`) — declared but no implementation.
- **`m_ui_element__typed_handler__text_box__alphanumeric`** (`ui/ui_text_box.h`) — declared but no implementation.
- **`set_c_str_of__ui_text_with__const_c_str`** / **`buffer_c_str_of__ui_text`** / **`clear_c_str_of__ui_text`** / **`insert_c_str_into__ui_text`** (`ui/ui_text.h`) — declared but no implementation.
- **`m_ui_element__transformed_handler__text__centered`** (`ui/ui_text.h`) — declared but no implementation.
- **`m_ui_draggable__dropped_handler__default`** (`ui/ui_draggable.h`) — declared but no implementation.
- **`register_game_action__hitbox_for__server`** / **`initialize_game_action_for__hitbox`** (`game_action/core/hitbox/game_action__hitbox.h`) — declared but no implementation.
- **`m_process__game_action__tcp_connect__begin`** / **`m_process__game_action__tcp_connect__begin__init`** (`game_action/core/tcp/game_action__tcp_begin_connect.h`) — declared but no implementation.
- **`m_process__game_action__tcp_connect__inbound`** / **`receive_game_action__connect`** (`game_action/core/tcp/game_action__tcp_connect.h`) — declared but no implementation.
- **`initialize_game_action_for__tcp_connect__accept`** (`game_action/core/tcp/game_action__tcp_connect__accept.h`) — declared but no implementation.
- **`m_process__game_action__tcp_delivery__inbound`** (`game_action/core/tcp/game_action__tcp_delivery.h`) — declared but no implementation.
- **`m_process__game_action__bad_request__inbound`** (`game_action/core/game_action__bad_request.h`) — declared but no implementation.
- **`m_process__game_action__global_space__store`** (`game_action/core/global_space/game_action__global_space__store.h`) — declared but no implementation.
- **`m_process__game_action__global_space__request__outbound_client`** / **`__outbound_client__init`** / **`__outbound_server`** (`game_action/core/global_space/game_action__global_space__request.h`) — declared but no implementation.
- **`initialize_game_action_for__global_space__request`** — declared but no implementation.
- **`initialize_game_action_for__global_space__store`** — declared but no implementation.
- **`initialize_game_action_for__input`** (`game_action/core/input/game_action__input.h`) — declared but no implementation.
- **`m_process__game_action__world__load_client__outbound`** (`game_action/core/world/game_action__world__load_client.h`) — declared but no implementation.
- **`get_p_timeout_timer_u32_from__ga_global_space__request`** (`types/core/game_action/global_space/ga_type__global_space__request.h`) — declared but no implementation.
- **`get_p_the_kind_of_hitbox_from__ga_collisions`** (`types/core/game_action/collisions/ga_types__collisions.h`) — declared but no implementation.
- **`get_p_scene_from__scene_manager`** (`scene/scene_manager.c`) — implementation exists but has redundant inner bounds check.
- **`is_graphics_window_NOT_from__this_graphics_window_manager`** (`rendering/graphics_window_manager.c`) — doesn't null-check `p_graphics_window` before pointer arithmetic.

### F. Aliasing Bugs (Pointer / Union Misuse)

Functions where pointers or unions are used incorrectly:

- **`get_p_sprite_by__uuid_from__sprite_context`** (`rendering/sprite_context.h`) — calls `dehash_identitier_u32_in__contigious_array` without checking if the result is deallocated.
- **`get_pV_hitbox_manager_from__hitbox_context`** (`collisions/hitbox_context.h`) — dereferences `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context(...)` without null check, then accesses `->pVM_hitbox_manager`.
- **`is_p_serialized_field__linked`** (`serialization/serialized_field.h`) — accesses `p_serialized_field__serialization_header->uuid` through a union member that might not be a `Serialization_Header*`.
- **`initialize_serialized_field`** (`serialization/serialized_field.c`) — sets `sizeof(Serialized_Field)` as `size_of__struct`, but the data being serialized is `p_serialized_field__data`, not a `Serialized_Field`.
- **`cstr_to_i16/i8/u16/u8__limit_n`** (`lav_string.h`) — assigns `bool` return of `cstr_to_i32__limit_n` to an integer variable, then casts to the target type. The parsed value is lost; only the success flag is used as the value.
- **`get_p_serialization_header_from__contigious_array`** — uses `p_serialization_headers->size_of__struct` to compute the offset, but `size_of__struct` might not be set correctly for all elements in the array.

### G. Coupling / Shared State Concerns

Functions where coupling or shared mutable state creates fragility:

- **`broadcast_game_action`** (`game.c`) — directly calls `dispatch_game_action_for__client` for the local client, then iterates all clients. The local client is dispatched twice if it appears in the client pool.
- **`dehash_from__serialization_pool`** (`serialization/serialization_pool.h`) — name implies "remove from hash" but only performs a lookup, creating a **Translation Gap** between name and behavior.
- **`allocate_by_hash_in__serialization_pool`** (`serialization/serialization_pool.h`) — name implies "allocate by hash" but only sets the uuid; doesn't mark as allocated or update any allocation counter.
- **`get_p_local_space_manager_thats__closest_to__this_position`** (`game.c`) — O(N) scan with no caching; acknowledged in TODO.
- **`poll_collision_resolver_aabb`** (`collisions/collision_resolver_aabb.c`) — manually unrolls 8 neighbor checks with copy-paste errors; should use a loop over neighbor offsets.
- **`f_sort_heuristic__sprite_render_record`** — inconsistent comparison direction violates the **Conservation Law** of sort heuristics (must be a consistent total order).
- **`is_local_space_manager__loaded`** — hardcodes a formula for counting boundary spaces; tightly coupled to chunk dimensions.
- **`get_quantity_of__available_sort_lists/nodes_in__sort_list_manager`** — swapped counters create a **State Desync** between available counts and actual allocations.

---

## 2. Impact Assessment

### Cross-cutting Dependencies

The **`dehash_identitier_u32_in__contigious_array`** and **`get_next_available__uuid_in__contiguous_array`** functions in `serialization/hashing.c` are the **Single Source of Truth (SSOT)** for UUID-based lookup across the entire codebase. They are called from:

- `serialization/serialization_pool.h` — `dehash_from__serialization_pool`, `allocate_by_hash_in__serialization_pool`
- `serialization/hashing.h` — `allocate_serialization_header`, `allocate_serialization_header_with__uuid_branding`, `get_next_available__random_uuid_in__contiguous_array`, `has_uuid_in__contiguous_array`
- `rendering/graphics_window_manager.c` — `get_p_graphics_window_by__uuid_from__graphics_window_manager`
- `rendering/sprite_context.h` — `get_p_sprite_manager_by__uuid_from__sprite_context`
- `rendering/sprite_manager.c` — `get_p_sprite_by__uuid_from__sprite_manager`
- `multiplayer/tcp_socket_manager.h` — `get_p_tcp_socket_for__this_uuid`
- `multiplayer/tcp_socket_manager.c` — `allocate_tcp_socket_from__tcp_socket_manager`
- `process/process_manager.h` — `get_p_process_by__uuid`
- `process/process_manager.c` — `allocate_process_in__process_manager`
- `collisions/collision_node_pool.h` — `get_p_collision_node_by__uuid_64_from__collision_node_pool`
- `inventory/inventory_manager.h` — `get_inventory_by__uuid_in__inventory_manager`
- `entity/entity_manager.c` — `allocate_entity_in__entity_manager`, `allocate_entity_with__this_uuid_in__entity_manager`
- `game.c` — `get_p_client_by__uuid_from__game`
- `sorting/sort_list/sort_list_manager.c` — `allocate_sort_list_in__sort_list_manager`
- `graphics_window_manager.h` — `allocate_graphics_window_from__graphics_window_manager`

The hashing bug (rounding uuid down to multiple of array length, causing `poll_for__uuid_collision` to always start at index 0) **invalidates the hash-based lookup invariant** for all of these callers. Correcting it will change which slot each UUID maps to, potentially breaking any code that relies on the current (buggy) slot assignment.

### Numerics / Fixed-Point Coupling

The **`numerics.h`** clamped arithmetic functions (`subtract_u8/u16/u32__clamped`, `multiply_u8/u16/u32__clamped`) are used throughout:
- `timer.h` — `poll_timer_by__this_duration_u32` uses `subtract_u32__no_overflow` (not the clamped variant, so unaffected)
- `inventory/item_stack.c` — `add_u8__clamped` and `subtract_u8__no_overflow` are used in `merge_p_item_stacks` and `remove_quantity_of_items_from__item_stack`
- `vectors.h` — `add_u32__no_overflow` is used in `get_distance_squared_of__vector_3i32__no_overflow`

Correcting `subtract_u8/u16/u32__clamped` will affect any caller that relies on the current (inverted) clamping behavior. The `multiply_u8/u16/u32__clamped` overly conservative check affects sprite rendering, UI layout, and any code that multiplies small fixed-point values.

### Serialization Header Coupling

The `initialize_serialization_header` function is declared in `serialization_header.h` but its implementation is missing from `serialization_header.c`. This function is called by:
- `initialize_serialization_header__contiguous_array` (same file)
- `initialize_serialization_header_for__deallocated_struct` (inline in header)
- `initialize_message` (log/message.c)
- `initialize_tcp_socket` (multiplayer/tcp_socket.c)
- `initialize_entity` (entity/entity.c)
- `initialize_item_stack` (inventory/item_stack.c)
- `initialize_serialized_field` (serialization/serialized_field.c)
- `allocate_serialization_header_with__this_uuid` (hashing.h, inline)
- `allocate_serialization_header` (hashing.h, inline)
- `allocate_serialization_header_with__this_uuid__u64` (hashing.h, inline)
- `allocate_serialization_header__u64` (hashing.h, inline)
- `allocate_serialization_header_with__uuid_branding__u64` (hashing.h, inline)

If `initialize_serialization_header` is missing, the entire serialization system fails to link.

### Game Action Dispatch Coupling

The `dispatch_game_action__*` inline functions in `game_action/core/` headers create stack-allocated `Game_Action` structs and pass pointers to `dispatch_game_action`. This couples the dispatch mechanism to the assumption that the `Game_Action` pointer is consumed synchronously. If any backend stores the pointer for asynchronous processing, it will reference freed stack memory.

### UI Flag Coupling

The `is_ui_flags__needing_update` function references `UI_FLAGS__BIT_IS_NEEDING_UPDATE`, which is **not defined** in `defines.h`. This means any translation unit that includes `ui_flags.h` will fail to compile. This is a **Conservative** compilation blocker.

### Process Table Coupling

The `get_quantity_of__processes_in__process_priority_table_entry` function returns `oldest - youngest` instead of `youngest - oldest`. This affects:
- `get_quantity_of__processes_in__process_table` (process_table.c) — uses the per-entry count
- `poll_process_manager` (process_manager.c) — indirectly affected

Correcting this will fix the process count reporting but may expose latent bugs in callers that compensated for the wrong count.

### Rendering Sort Coupling

The `f_sort_heuristic__sprite_render_record` function has inconsistent comparison directions (`>` for z, `<` for y). This violates the **Conservation Law** of sort heuristics (must provide a consistent total order). Correcting it will change sprite rendering order, potentially affecting visual output.

### Timer Coupling

The `poll_timer_u32/u16/u8` functions have an off-by-one issue where the timer doesn't decrement on the call that detects it's elapsed. This affects:
- `game.c` — `poll__game_tick_timer` uses timer logic
- `degree.c` — `get_angle_between__vectors_3i32` doesn't use timers directly
- Animation timers throughout the rendering system
- Audio effect timers

### Input Coupling

The `is_input__none_released/held/pressed` functions always return false due to `& INPUT_NONE` (0). Any code checking "no input" will always get false, meaning the "no input" state is never detected. This affects input handling logic throughout the game loop.

---

## 3. Resolution Assessment

### Phase 1: Critical Linkage Failures (Stub-real Divergence)

**Priority: Highest** — these prevent compilation or cause runtime aborts.

1. **`allocate_room_in__structure_manager`** — Implement in a new `core/source/world/structures/structure_manager.c` file, or remove the declaration if the function is unused (the review notes it has no callers).
2. **`get_chunk_at__index_from__chunk_pool`** — Add the missing public API function to `core/include/world/chunk_pool.h` and `core/source/world/chunk_pool.c`, delegating to the internal helper `get_p_chunk_by__index_from__chunk_pool`.
3. **`poll_for__collisions`** — Add the declaration to `core/include/world/local_space.h` and implement it, or remove the reference if it was moved.
4. **`manage_game`** — Implement in `game.c` or remove the declaration.
5. **`print_console` / `clear_console`** — Implement in a new `core/source/debug/console.c` or remove declarations.
6. **`stat_chunk_directory`** / **`is_region_in__directory`** — Implement in `core/source/world/serialization/` or remove.
7. **`register_core_items_into__item_manager`** — Implement the actual item registration logic instead of the `debug_warning("impl")` stub.
8. **`poll_world_for__scrolling`** / **`save_world`** — Implement actual logic instead of `debug_abort("impl")`.
9. **`m_load_scene_as__main_handler` / `m_unload_scene_as__main_handler`** — Implement actual scene load/unload logic.
10. **`is_in_multiplayer_game` / `is_host` / `get_user_id`** — Implement in a `.c` file; fix `USER_ID` type.
11. **`handle_pending_connection`** / **`m_poll_tcp_socket_manager_as__server__default` / `__client__default`** — Implement.
12. **`m_process__save_local_space_node` / `m_process__save_chunk` / `m_process__save_collision_node`** — Implement.
13. **`register_chunk_generators`** / **`register_hitbox_managers`** / **`register_entities`** — Implement.
14. **`activate_serialization_request`** — Implement.
15. **`stat_game_data_file` / `append_path`** — Implement.
16. **`initialize_serialization_header`** / **`initialize_serialization_header__uuid_64`** / **`initialize_serialization_header__contiguous_array`** / **`__contiguous_array__uuid_64`** / **`get_p_serialization_header_from__contigious_array`** / **`get_next_available_p_serialization_header`** / **`get_p_serialization_header_from__contigious_array__uuid_64`** / **`get_next_available_p_serialization_header__uuid_64`** — Implement in `serialization_header.c`.
17. **`is_identifier_u32_matching__serialization_header`** / **`is_identifier_u64_matching__serialization_header`** — Implement (currently only declared).
18. **All missing collision node, hitbox, tile logic, local space, global space, entity, game action, UI, and rendering implementations** — Implement or remove declarations.

### Phase 2: Mode Confusion / Inverted Logic

**Priority: High** — these cause incorrect runtime behavior.

1. **`is_input__none_released/held/pressed`** — Change `& INPUT_NONE` to `== INPUT_NONE`.
2. **`is_position_within__camera_fulcrum`** — Change `>` to `<=` (or invert the entire condition).
3. **`subtract_u8/u16/u32__clamped`** — Change `subtraction > min__u8` to `subtraction < min__u8`.
4. **`set_ui_element_as__snapped_y_axis`** — Change `&= ~` to `|=`.
5. **`is_ui_flags__focused`** — Change to check `UI_FLAGS__BIT_IS_FOCUSED`.
6. **`is_ui_element__using_ui_tile_span`** — This is actually correct (returns true when NOT using sprite). But `does_ui_element_have__compose_handler` uses it correctly. The issue is the naming is confusing. Consider renaming or clarifying.
7. **`add_angles`** — Change `& ANGLE__MASK` to `& (ANGLE__360 - 1)` or `& 0x1FF` (9 bits for angles up to 511).
8. **`is_p_item_stack___full`** — Fix the logic to check `quantity == max` (or remove if it's a duplicate of `is_p_item_stack__full`).
9. **`get_p_local_space_manager_thats__closest_to__this_position`** — Initialize `p_local_space_manager__closest` to `0`.
10. **`broadcast_game_action`** — Fix the for loop condition to `index_of__client < get_max_quantity_of__clients_for__game(p_game)`.
11. **`is_client__failed_to_load`** — Remove the `set_client_as__inactive` side effect.
12. **`unbind_tcp_socket`** — Fix the inverted error check: `if (PLATFORM_tcp_close_socket(...))` instead of `if (!PLATFORM_tcp_close_socket(...))`.
13. **`m_game_action_handler__receive__multiplayer`** — Return the result of `receive_game_action_for__client`.
14. **`add_process_to__process_table`** — Add the process to the priority table entry when it's empty.
15. **`poll_process_manager`** — Increment `ticks_elapsed` in the loop.
16. **`get_quantity_of__processes_in__process_priority_table_entry`** — Change to `youngest - oldest` (or `youngest - oldest + 1`).
17. **`get_quantity_of__available_sort_lists/nodes`** — Fix the swapped counters.
18. **`release_sort_list_in__sort_list_manager`** — Change `+=` to `-=`.
19. **`release_sort_nodes_in__sort_list_manager`** — Change `SORT_LIST__MAXIMUM_QUANTITY_OF` to `SORT_NODE__MAXIMUM_QUANTITY_OF` and `set_sort_node_as__allocated` to `set_sort_node_as__deallocated`.
20. **`set_the_type_of__room`** — Change return type from `Room_Type__u16` to `void`.
21. **`set_tile_logic_record_as__*` functions** — Change return type from `bool` to `void`.

### Phase 3: Boundary Condition / Overflow Issues

**Priority: High** — these can cause crashes or data corruption.

1. **`set_item_stack`** — Add clamping or change parameter types to `Quantity__u8`.
2. **`add_item_to__inventory`** — Use `add_u8__clamped` instead of raw `+` before `clamp__u8`.
3. **`get_p_item_stack_from__inventory`** — Add bounds check on the extracted index.
4. **`get_p_local_space_by__index_from__local_space_manager`** — Change `>` to `>=`.
5. **`is_local_space_manager__loaded`** — Fix the edge-counting formula.
6. **`get_p_graphics_window_by__index_in_ptr_array_from__manager`** — Add bounds check.
7. **`accept_socket_on__tcp_socket_manager__ipv4`** — Check if `allocate_tcp_socket_from__tcp_socket_manager` returns null.
8. **`close_socket_on__tcp_socket_manager__ipv4`** — Initialize `p_ptr_tcp_socket__being_release` and `p_ptr_tcp_socket__last` to null.
9. **`allocate_by_hash_in__serialization_pool`** — Check if `dehash_identitier_u32_in__contigious_array` returns null.
10. **`get_next_available__uuid_in__contiguous_array`** — Don't round down the uuid before hashing.
11. **`merge_identifiers_u32`** — Fix the `MASK(33 - bits__left)` formula.
12. **`receive_bytes_over__tcp_socket`** — Return actual bytes received, not `MAX_SIZE * count`.
13. **`progress_timer__u32`** — Handle `start__u32 == 0` case.
14. **`poll_timer_u32/u16/u8`** — Fix the short-circuit so the timer decrements correctly.
15. **`get_p_entity_from__world_using__3i32F4`** — Add null check for `p_global_space`.
16. **`get_p_serialization_header_from__contigious_array`** — Implement with proper bounds checking.
17. **`set_tile_of__chunk`** — Fix the index calculation to match `get_p_tile_from__chunk`.
18. **`get_p_tile_from__chunk_using__u8`** — Fix the z-stride to use `CHUNK__WIDTH * CHUNK__HEIGHT` consistently.
19. **`cstr_to_i32__limit_n`** — Fix the `goto` and sign handling.
20. **`cstr_to_i16/i8/u16/u8__limit_n`** — Fix the return value / output parameter confusion.
21. **`get_index_of__sort_node_in__sort_list`** — Return `INDEX__UNKNOWN__SORT_NODE` on null input.
22. **`allocate_sprite_from__sprite_manager`** — Check if `p_PLATFORM_sprite` is non-null before calling `PLATFORM_release_sprite`.
23. **`release_sprite_from__sprite_manager`** — Fix the do-while loop bounds check.
24. **`get_p_sprite_animation_group_from__sprite_context`** — Change `Sprite_Animation_Kind__Unknown` to `Sprite_Animation_Group_Kind__Unknown`.
25. **`is_graphics_window_NOT_from__this_graphics_window_manager`** — Add null check for `p_graphics_window`.

### Phase 4: Type / Precision Mismatches

**Priority: Medium** — these cause incorrect results in specific cases.

1. **`vector_3i32F4_to__vector_3u8`** — Use `i32F4_to__i32()` instead of `>>`.
2. **`vector_3i32F4_to__vector_3i16F8`** — Use proper conversion functions.
3. **`vector_3i32_to__tile_vector`** — Fix parameter type to match name (or vice versa).
4. **`is_vector_3i32F20_within__squared_distance_i32F4`** — Fix parameter type to `i32F4`.
5. **`get_distance_squared_of__vector_3i32__no_overflow`** — Fix parameter name from `u64` to `u32`.
6. **`divide_into__i32F4`** — Fix return type to `i32F4` or rename function.
7. **`offset_vector_by__direction`** — Use `i32_to__i32F4(1)` instead of `++`/`--`.
8. **`VECTOR__3i32__1_n1_0`** / **`VECTOR__3i32__n1_n1_0`** — Fix the x-component to `-1`.
9. **`get_p_item_stack_alloc_spec_by__index_from__item_stack_manager`** — Make `static inline` or move to `.c` file.
10. **`set_item_stack`** — Change parameter types to match struct fields.
11. **`is_quantity_u32__out_of_bounds`** — Change parameter type to `Quantity__u32`.
12. **`is_ui_flags__needing_update`** — Define `UI_FLAGS__BIT_IS_NEEDING_UPDATE` or remove the function.
13. **`initalize_item_stack_with__item_stack_manager`** — Fix typo in function name.
14. **`release_item_stack_allocation_specification_in__item_stack_manager`** — Fix `NDBEUG` to `NDEBUG`.
15. **`PLATFORM_tcp_recieve`** — Fix typo to `PLATFORM_tcp_receive`.

### Phase 5: State Desync / Shared State

**Priority: Medium to High** — these cause inconsistent state.

1. **`get_pseudo_random_i32__non_intrusively`** — Save and restore the global RNG state properly.
2. **`get_pseudo_random_i32_with__xy__intrusively`** — Fix state management.
3. **`get_random__uuid_u32`** — Handle signed/unsigned conversion.
4. **`get_random__uuid_u64`** — Use the intrusive variant or fix state management.
5. **`get_p_latest_allocated_process_from__process_manager`** — Document the consume side-effect or change the API.
6. **`initialize_entity`** — Use a proper uuid instead of the zeroed `_serialization_header.uuid`.
7. **`dispatch_game_action__*`** inline functions — Don't use stack-allocated `Game_Action`; allocate from the manager instead.
8. **`run_sort__once`** — Add `return` before `p_sort_list->m_sort(p_sort_list)`.
9. **`f_sort_heuristic__sprite_render_record`** — Make comparison direction consistent.
10. **`release_sort_list_in__sort_list_manager`** — Fix `+=` to `-=`.

### Phase 6: Serialization Hashing Fixes

**Priority: High** — affects all UUID-based lookups.

1. **`get_next_available__uuid_in__contiguous_array`** — Don't round down the uuid before hashing; use the uuid directly for the hash bucket.
2. **`get_next_available__uuid_in__contiguous_array__uuid_64`** — Same fix.
3. **`poll_for__uuid_collision`** — Ensure the sentinel `INDEX__UNKNOWN__u32` cannot collide with valid indices.
4. **`dehash_identitier_u32_in__contigious_array`** — Simplify the redundant loop.
5. **`dehash_identitier_u64_in__contigious_array`** — Same simplification.

### Phase 7: Documentation / Comment Fixes

**Priority: Low** — these don't affect runtime but cause confusion.

1. **`put_char_into__message`** — Fix the `.c` comment to match the header.
2. **`send_bytes_over__tcp_socket`** — Fix the header doc or add return value.
3. **`unbind_tcp_socket`** — Fix the header doc or add return value.
4. **`get_latest__delivery_from__tcp_socket`** — Fix the header doc or return type.
5. **`receive_bytes_over__tcp_socket`** — Fix the header doc or return value.
6. **`m_entity_enable_handler__default`** / **`m_entity_disable_handler__default`** — Fix debug error messages.
7. **`link_ui_element_to__this_ui_element`** — Add missing `return` after self-link check.

---

## 4. Test Verification Checklist

### Existing Test Coverage

A survey of the `tests/` directory reveals limited test coverage for the flagged functions. Most tests appear to be integration-level rather than unit tests. Key findings:

- **No unit tests** exist for `numerics.h` clamped arithmetic functions (`subtract_u8/u16/u32__clamped`, `multiply_u8/u16/u32__clamped`, `add_u8/u16/u32__clamped`).
- **No unit tests** exist for `vectors.h` conversion functions or `tile_vectors.h` normalization functions.
- **No unit tests** exist for `degree.h` angle functions (`add_angles`, `subtract_angles`, `get_middle_angle`).
- **No unit tests** exist for `random.c` pseudo-random functions.
- **No unit tests** exist for `timer.h` polling functions.
- **No unit tests** exist for `lav_string.h` conversion functions.
- **No unit tests** exist for `input.h` `is_input__none_*` functions.
- **No unit tests** exist for `serialization/hashing.h` UUID functions.
- **No unit tests** exist for `sort/sort_list/` functions.
- **No unit tests** exist for `inventory/` functions.
- **No unit tests** exist for `multiplayer/` TCP socket functions.
- **No unit tests** exist for `process/` functions.
- **No unit tests** exist for `scene/` functions.
- **No unit tests** exist for `entity/` functions.
- **No unit tests** exist for `collisions/` functions.
- **No unit tests** exist for `ui/` functions.

### Recommended New Tests

Using terminology-based test recommendations:

1. **Property Based Testing** for `subtract_u8/u16/u32__clamped` — verify that `subtract(a, b, min)` always returns a value >= min, and equals `a - b` when `a >= b` and `a - b >= min`.

2. **Property Based Testing** for `multiply_u8/u16/u32__clamped` — verify that the result never exceeds the clamp value, and that valid multiplications (where the product doesn't overflow) are not incorrectly clamped.

3. **Round Trip Check** for `add_angles` / `subtract_angles` — verify that `subtract_angles(add_angles(a, b), b) == a` (with proper angle wrapping).

4. **Equivalence Check** for `vector_3i32F4_to__vector_3u8` — verify that the result matches `vector_3i32F4_to__vector_3i32` followed by casting to u8.

5. **Fuzzing** for `cstr_to_i32__limit_n` — test with various string inputs including signs, non-numeric characters, overflow values, and edge cases.

6. **Property Based Testing** for `get_next_available__uuid_in__contiguous_array` — verify that the returned UUID maps to a valid slot in the array.

7. **Round Trip Check** for `poll_for__uuid_collision` / `dehash_identitier_u32_in__contigious_array` — verify that a UUID allocated via `get_next_available__uuid_in__contiguous_array` can be found via `dehash_identitier_u32_in__contigious_array`.

8. **Property Based Testing** for `poll_timer_u32` — verify that the timer fires exactly `start` polls after initialization.

9. **Equivalence Check** for `is_input__none_released/held/pressed` — verify that the function returns true only when no input flags are set.

10. **Mutation Testing** for `run_sort__once` — verify that the return value of `m_sort` is properly propagated.

11. **Property Based Testing** for `sort_graphic_windows_in__graphic_window_manager` — verify that the sort produces a consistent ordering (parent before children, siblings by Z).

12. **Round Trip Check** for `serialize_inventory` / `deserialize_inventory` — verify that deserializing a serialized inventory produces an identical inventory.

13. **Fuzzing** for `populate_ipv4_address` — test with various IP address strings including edge cases (0.0.0.0, 255.255.255.255, invalid formats).

14. **Property Based Testing** for `get_quantity_of__processes_in__process_priority_table_entry` — verify that the count matches the actual number of allocated processes in the entry.

15. **Equivalence Check** for `get_p_local_space_by__index_from__local_space_manager` — verify that out-of-bounds indices return null in debug mode.

### Blast Radius: Test Impact

- **High** — Fixes to `numerics.h`, `vectors.h`, `tile_vectors.h`, `chunk_vectors.h`, and `degree.h` affect virtually every system that uses fixed-point math. All game logic, rendering, collision detection, and world management depend on these.
- **High** — Fixes to `serialization/hashing.h` and `serialization/serialization_header.h` affect all UUID-based lookups across the entire codebase.
- **Medium** — Fixes to `input.h` affect all input handling.
- **Medium** — Fixes to `timer.h` affect all timed operations (animations, audio, game ticks).
- **Medium** — Fixes to `process/` affect all asynchronous operations (serialization, game actions, world loading).
- **Medium** — Fixes to `inventory/` affect all item management.
- **Low to Medium** — Fixes to `ui/` affect UI rendering and interaction.
- **Low to Medium** — Fixes to `rendering/` affect graphics rendering.
- **Low** — Fixes to `game_action/` affect network message dispatch.

A **phased approach** is recommended: fix and test utility functions first (numerics, vectors, timers), then serialization, then higher-level systems.

---

## 5. Blast Radius Summary

- **Files affected:** ~50+ header files and ~30+ source files across all major subsystems.
- **Behavior-preserving for current callers:** No. Many functions have inverted logic or wrong return values that callers may have compensated for. Correcting these will change runtime behavior.
- **Phased approach needed:** Yes. The dependency graph is: `defines.h` → `numerics.h` → `vectors.h` → `tile_vectors.h` / `chunk_vectors.h` → `world/` → `entity/` / `inventory/` / `rendering/` → `game_action/` → `game.h` / `client.h`. Serialization hashing is a cross-cutting dependency used by almost everything.
- **De facto contracts invalidated:**
  - `is_input__none_released/held/pressed` always returning false — any code checking for "no input" is broken.
  - `is_position_within__camera_fulcrum` returning true when outside — camera culling logic is inverted.
  - `subtract_u8/u16/u32__clamped` clamping in the wrong direction — any code using these for minimum bounds is broken.
  - `add_angles` wrapping at 32 instead of 512 — angle arithmetic is broken for all angles > 31.
  - `get_next_available__uuid_in__contiguous_array` always starting collision resolution at index 0 — hash distribution is broken.
  - `get_quantity_of__available_sort_lists/nodes` swapped — allocation limits are wrong.
  - `get_quantity_of__processes_in__process_priority_table_entry` returning negative — process counting is broken.
  - `poll_process_manager` not incrementing `ticks_elapsed` — all processes run every tick.
  - `run_sort__once` not returning the sort result — callers can't determine if sorting is complete.
  - `broadcast_game_action` infinite loop — the for loop has no proper termination condition.
  - `get_p_local_space_manager_thats__closest_to__this_position` returning uninitialized pointer — potential crash.
  - `quit_scene_state_machine` null pointer dereference — crashes when no active scene.
  - `set_bit_in__bitmap` — the `~` operator on u32 may cause issues on some compilers (though typically truncated correctly).
  - `cstr_to_i16/i8/u16/u8__limit_n` treating bool as value — all string-to-integer conversions for these types produce incorrect results.
  - `is_ui_flags__needing_update` referencing undefined macro — compilation failure for any file including `ui_flags.h`.
  - `set_tile_of__chunk` using different index formula than `get_p_tile_from__chunk` — tiles written to wrong location.
  - `is_p_item_stack___full` (three underscores) checking "not full" — inventory fullness checks are inverted.
  - `set_ui_element_as__snapped_y_axis` clearing instead of setting — slider snapping is broken.
  - `unbind_tcp_socket` inverted error check — socket cleanup fails silently.
  - `receive_bytes_over__tcp_socket` returning wrong byte count — TCP receive accounting is broken.
  - `is_client__failed_to_load` modifying state — query function has side effects.
  - `dispatch_game_action__*` stack-allocating Game_Action — potential use-after-free if stored.
  - `initialize_entity` using zeroed uuid — entity UUIDs are always 0.
  - `allocate_sprite_from__sprite_manager` calling release on uninitialized pointer — potential crash.
  - `close_socket_on__tcp_socket_manager__ipv4` uninitialized pointer variables — potential crash.
  - `get_p_sprite_animation_group_from__sprite_context` using wrong enum for bounds check — potential out-of-bounds access.
