initialize_scene_manager — core/source/scene/scene_manager.c

Resets a Scene_Manager struct to its initial/default state by zeroing all scene serialization headers, initializing each scene in the array, and clearing the active scene pointer.

Pre-conditions:
1. p_scene_manager must be a non-null pointer to a writable Scene_Manager object.

Post-conditions:
1. All Scene entries in p_scene_manager->scenes have their serialization headers initialized (memset to 0, then uuid set to IDENTIFIER__UNKNOWN__u32 and size set to sizeof(Scene)).
2. Each Scene in the array has been individually initialized via initialize_scene, setting all handler pointers to 0, p_parent_scene to 0, p_scene_data to 0, and is_active to false.
3. p_scene_manager->p_active_scene is set to 0 (null).

Correctness Verdict: Correct

Semantic Alignment:
This is a Lavender-style initialization (pool cleanup), not RAII. The function resets the Scene_Manager to its initial conditions by clearing all scenes and the active scene pointer. The implementation correctly:
- Initializes the serialization headers for the contiguous array of scenes
- Iterates through all Scene_Kind__Unknown scenes and calls initialize_scene on each
- Sets p_active_scene to 0

All fields of the Scene_Manager struct are addressed: the scenes array is fully initialized, and p_active_scene is set to null.

Implementation Correctness:
Type compatibility — the cast (Serialization_Header *)p_scene_manager->scenes is valid because Scene has Serialization_Header as its first member (_serialization_header). The sizeof(Scene) is passed as size_of__struct, which is correct. The loop variable Quantity__u8 scene_index is compared against Scene_Kind__Unknown (an enum value). The loop iterates from 0 to Scene_Kind__Unknown - 1, which correctly covers all valid scene indices.
No undefined behavior — no null dereference (the function assumes p_scene_manager is valid, which is the caller's responsibility). No out-of-bounds access — the loop bounds are correct. The get_p_scene_from__scene_manager function is called with valid indices within the loop range.
No validation is needed at this level — this is a low-level initialization function. The caller is responsible for ensuring p_scene_manager is valid.

Side Effects:
- Mutates p_scene_manager->scenes array: all scene entries are zeroed and their serialization headers initialized.
- Mutates p_scene_manager->p_active_scene: set to 0 (null).
- Calls initialize_scene on each scene, which mutates each Scene struct's fields.
