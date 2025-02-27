#include "world/global_space.h"
#include "defines.h"
#include "serialization/serialization_header.h"

void initialize_global_space(
        Global_Space *p_global_space) {
    memset(p_global_space,
            0,
            sizeof(Global_Space));
    initialize_serialization_header_for__deallocated_struct__uuid_64(
            &p_global_space->_serialization_header, 
            sizeof(Global_Space));
}

void initialize_global_space_as__allocated(
        Global_Space *p_global_space,
        Identifier__u64 uuid_64) {
    memset(p_global_space,
            0,
            sizeof(Global_Space));
    initialize_serialization_header__uuid_64(
            &p_global_space->_serialization_header, 
            uuid_64, 
            sizeof(Global_Space));
    p_global_space->quantity_of__references = 1;
}
