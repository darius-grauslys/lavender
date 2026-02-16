#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "platform_defines.h"
#include "serialization/serialization_header.h"
#include "types/implemented/scene_kind.h"
#include <scene/scene.h>
#include <scene/scene_manager.h>

void initialize_scene_manager(
        Scene_Manager *p_scene_manager) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)p_scene_manager->scenes, 
            Scene_Kind__Unknown, 
            sizeof(Scene));

    p_scene_manager->p_active_scene = 0;

    for (Quantity__u8 scene_index=0;
            scene_index
            <Scene_Kind__Unknown;
            scene_index++) {
        initialize_scene(
                get_p_scene_from__scene_manager(
                    p_scene_manager, 
                    scene_index)
                );
    }
}

void register_scene_into__scene_manager(
        Scene_Manager *p_scene_manager,
        Scene_Kind the_kind_of_scene_to__register,
        m_Load_Scene m_load_scene,
        m_Enter_Scene m_enter_scene,
        m_Unload_Scene m_unload_scene) {
    Scene *p_scene =
        get_p_scene_from__scene_manager(
                p_scene_manager, 
                the_kind_of_scene_to__register);

    if (!p_scene) {
        debug_warning("Did you forget to update the Scene_Kind enum?");
        debug_error("register_scene_into__scene_manager p_scene == 0.");
        return;
    }

    if (is_scene__valid(p_scene)) {
        debug_warning("register_scene_into__scene_manager, overwriting scene: %d",
                the_kind_of_scene_to__register);
    }

    p_scene->m_load_scene_handler = 
        m_load_scene;
    p_scene->m_enter_scene_handler = 
        m_enter_scene;
    p_scene->m_unload_scene_handler = 
        m_unload_scene;
}

Scene *get_p_scene_from__scene_manager(
        Scene_Manager *p_scene_manager,
        Scene_Kind the_kind_of__scene) {
    if (the_kind_of__scene >= Scene_Kind__Unknown) {
        if (the_kind_of__scene > Scene_Kind__Unknown) {
            debug_error("get_p_scene_from__scene_manager, invalid scene kind received, returning null.");
        }
        return 0;
    }
    return &p_scene_manager->scenes[the_kind_of__scene];
}

void set_active_scene_for__scene_manager(
        Scene_Manager *p_scene_manager,
        Scene_Kind the_kind_of__scene) {
    Scene *p_scene =
        get_p_scene_from__scene_manager(
                p_scene_manager, 
                the_kind_of__scene);
    if (p_scene_manager->p_active_scene) {
        p_scene_manager->p_active_scene->is_active = false;
    }
    p_scene_manager->p_active_scene = p_scene;
    if (p_scene) {
        p_scene->is_active = true;
    }
}

void quit_scene_state_machine(Scene_Manager *p_scene_manager) {
    if (!p_scene_manager->p_active_scene) {
        p_scene_manager->p_active_scene->is_active = false;
    }
    p_scene_manager->p_active_scene = 0;
}
