#ifndef OBJECT_H
#define OBJECT_H

#include "defines_weak.h"
#include <defines.h>

void activate_object(Game *p_game, Identifier__u32 uuid_of__object__u32);
void deactivate_object(Game *p_game, Identifier__u32 uuid_of__object__u32);

void prepare_object_for__teleport(Game *p_game, Identifier__u32 uuid_of__object__u32);
void conclude_object_for__teleport(Game *p_game, Identifier__u32 uuid_of__object__u32);

///
/// Prepares the object for teleportation, then dispatches a process
/// enqueued behind the m_process__teleportation_process which will
/// conclude the object for teleportation once unblocked.
///
Process *teleport_object(
        Game *p_game, 
        Identifier__u32 uuid_of__object__u32,
        Process *p_process__teleportation_process);

#endif
