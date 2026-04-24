#include "defines.h"
#include "defines_weak.h"
#include "entity/entity.h"

// GENERATE ALL INSTANCES OF NAME_OF_ENTITY IN LOWER CASE.

// GENERATE IF MISSING: --f-Dispose
// GENERATE IF PRESENT: --gen-f-Dispose
void m_entity_handler__dispose_NAME_OF_ENTITY(
        Entity *p_this_entity,
        Game *p_game,
        World *p_world) {
    // GEN-UPDATE-BEGIN
    m_entity_dispose_handler__default(
            p_this_entity, 
            p_game, 
            p_world);
    // GEN-UPDATE-END
}

// GENERATE IF MISSING: --f-Update
// GENERATE IF PRESENT: --gen-f-Update
void m_entity_handler__update_NAME_OF_ENTITY(
        Entity *p_this_entity,
        Game *p_game,
        World *p_world) {
    // GEN-UPDATE-BEGIN
    // GEN-UPDATE-END
}

// GENERATE IF MISSING: --f-Enable
// GENERATE IF PRESENT: --gen-f-Enable
void m_entity_handler__enable_NAME_OF_ENTITY(
        Entity *p_this_entity,
        Game *p_game,
        World *p_world) {
    // GEN-UPDATE-BEGIN
    m_entity_enable_handler__default(
            p_this_entity, 
            p_game, 
            p_world);
    // GEN-UPDATE-END
}

// GENERATE IF MISSING: --f-Disable
// GENERATE IF PRESENT: --gen-f-Disable
void m_entity_handler__disable_NAME_OF_ENTITY(
        Entity *p_this_entity,
        Game *p_game,
        World *p_world) {
    // GEN-UPDATE-BEGIN
    m_entity_disable_handler__default(
            p_this_entity, 
            p_game, 
            p_world);
    // GEN-UPDATE-END
}

// GENERATE IF MISSING: --f-Serialize
// GENERATE IF PRESENT: --gen-f-Serialize
PLATFORM_Write_File_Error m_entity_serialization_handler__NAME_OF_ENTITY(
        Entity *p_entity_self, 
        Game *p_game,
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Serialization_Request *p_serialization_request) {
    // GEN-SERIALIZE-BEGIN
    return PLATFORM_Write_File_Error__None;
    // GEN-SERIALIZE-END
}

// GENERATE IF MISSING: --f-Deserialize
// GENERATE IF PRESENT: --gen-f-Deserialize
PLATFORM_Read_File_Error *m_entity_deserialization_handler__NAME_OF_ENTITY(
        Entity *p_entity_self, 
        Game *p_game,
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Serialization_Request *p_serialization_request) {
    // GEN-SERIALIZE-BEGIN
    return PLATFORM_Read_File_Error__None;
    // GEN-SERIALIZE-END
}

// ALWAYS GENERATE:
void register_entity_NAME_OF_ENTITY_into__entity_manager(
        Entity_Manager *p_entity_manager) {
    // GEN-REGISTER-BEGIN
    Entity_Functions entity_functions__NAME_OF_ENTITY;
    memset(&entity_functions__NAME_OF_ENTITY,
            0,
            sizeof(Entity_Functions));

    // GENERATE IF PRESENT: --f-Update-Begin
    entity_functions__NAME_OF_ENTITY.m_entity_update_handler =
        0; // REPLACE WITH VALUE OF: --f-Update-Begin;

    // GENERATE IF NOT PRESENT: --f-Update-Begin
    entity_functions__NAME_OF_ENTITY.m_entity_update_handler =
        0; // REPLACE WITH VALUE OF: --f-Update; OR: m_entity_handler__update_NAME_OF_ENTITY;
    
    // GENERATE IF PRESENT: --gen-f-Dispose
    entity_functions__NAME_OF_ENTITY.m_entity_dispose_handler =
        0; // REPLACE WITH VALUE OF: --f-Dispose; OR: m_entity_handler__dispose_NAME_OF_ENTITY;

    // GENERATE IF PRESENT: --gen-f-Enable
    entity_functions__NAME_OF_ENTITY.m_entity_enable_handler =
        0; // REPLACE WITH VALUE OF: --f-Enable; OR: m_entity_handler__enable_NAME_OF_ENTITY;

    // GENERATE IF PRESENT: --gen-f-Disable
    entity_functions__NAME_OF_ENTITY.m_entity_disable_handler =
        0; // REPLACE WITH VALUE OF: --f-Disable; OR: m_entity_handler__disable_NAME_OF_ENTITY;

    // GENERATE IF PRESENT: --gen-f-Serialize
    entity_functions__NAME_OF_ENTITY.m_entity_serialize_handler =
        0; // REPLACE WITH VALUE OF: --f-Serialize; OR: m_entity_handler__serialize_NAME_OF_ENTITY;

    // GENERATE IF PRESENT: --gen-f-Deserialize
    entity_functions__NAME_OF_ENTITY.m_entity_deserialize_handler =
        0; // REPLACE WITH VALUE OF: --f-Deserialize; OR: m_entity_handler__deserialize_NAME_OF_ENTITY;

    register_entity_into__entity_manager(
            p_entity_manager, 
            Entity_Kind__NAME_OF_ENTITY, // First letter of each '_' seperated word uppercased.
            entity_functions__NAME_OF_ENTITY);
    // GEN-REGISTER-END
}
