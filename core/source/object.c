#include "object.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "types/implemented/object.h"

void activate_object(Game *p_game, Identifier__u32 uuid_of__object__u32) {
    f_Object_Handler f_object_handler = 0;
    for (Index__u8 index_of__object_handler = 0;
            (f_object_handler = array_of__object_handlers__activate_object[
            index_of__object_handler]) != 0;
            index_of__object_handler++) {
        if (!f_object_handler)
            break; // Safety redundancy

        f_object_handler(p_game, uuid_of__object__u32);
    }
}

void deactivate_object(Game *p_game, Identifier__u32 uuid_of__object__u32) {
    f_Object_Handler f_object_handler = 0;
    for (Index__u8 index_of__object_handler = 0;
            (f_object_handler = array_of__object_handlers__deactivate_object[
            index_of__object_handler]) != 0;
            index_of__object_handler++) {
        if (!f_object_handler)
            break; // Safety redundancy

        f_object_handler(p_game, uuid_of__object__u32);
    }
}

void prepare_object_for__teleport(Game *p_game, Identifier__u32 uuid_of__object__u32) {
    f_Object_Handler f_object_handler = 0;
    for (Index__u8 index_of__object_handler = 0;
            (f_object_handler = array_of__object_handlers__pre_teleport_object[
            index_of__object_handler]) != 0;
            index_of__object_handler++) {
        if (!f_object_handler)
            break; // Safety redundancy

        f_object_handler(p_game, uuid_of__object__u32);
    }
}

void conclude_object_for__teleport(Game *p_game, Identifier__u32 uuid_of__object__u32) {
    f_Object_Handler f_object_handler = 0;
    for (Index__u8 index_of__object_handler = 0;
            (f_object_handler = array_of__object_handlers__post_teleport_object[
            index_of__object_handler]) != 0;
            index_of__object_handler++) {
        if (!f_object_handler)
            break; // Safety redundancy

        f_object_handler(p_game, uuid_of__object__u32);
    }
}

void m_process__teleport_object(
        Process *p_this_process,
        Game *p_game) {
    Identifier__u32 uuid_of__object__u32 =
        p_this_process->process_valueA__i32;
    conclude_object_for__teleport(
            p_game, 
            uuid_of__object__u32);
    complete_process(p_this_process);
}

///
/// Prepares the object for teleportation, then dispatches a process
/// enqueued behind the m_process__teleportation_process which will
/// conclude the object for teleportation once unblocked.
///
Process *teleport_object(
        Game *p_game, 
        Identifier__u32 uuid_of__object__u32,
        Process *p_process__teleportation_process) {
    Process *p_process__teleport_object = 
        run_process(
                get_p_process_manager_from__game(p_game), 
                m_process__teleport_object, 
                PROCESS_PRIORITY__0_MAXIMUM, 
                PROCESS_FLAGS__NONE);
    if (!p_process__teleport_object) {
        debug_error("teleport_object, p_process__teleport_object == 0.");
        return 0;
    }
    prepare_object_for__teleport(
            p_game, 
            uuid_of__object__u32);

    enqueue_process(p_process__teleport_object, 
            p_process__teleportation_process);
}
