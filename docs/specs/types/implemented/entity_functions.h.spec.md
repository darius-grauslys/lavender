# Specification: core/include/types/implemented/entity_functions.h

## Overview

Template header that defines the `Entity_Functions` struct — the set of
function pointers that define an entity's behavior (update, dispose, enable,
disable, serialize, deserialize). This file is copied to the game project
directory by `tools/lav_new_project` and is meant to be extended by the
engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_ENTITY_FUNCTIONS` is not defined after
the `#include`, `defines.h` falls back to a built-in default.

## Dependencies

- `defines_weak.h` (for `m_Entity_Handler`, `m_Entity_Serialization_Handler`,
  `m_Entity_Deserialization_Handler`)

## Types

### Entity_Functions (struct)

    typedef struct Entity_Functions_t {
        m_Entity_Handler                m_entity_dispose_handler;
        m_Entity_Handler                m_entity_update_handler;
        m_Entity_Handler                m_entity_disable_handler;
        m_Entity_Handler                m_entity_enable_handler;
        m_Entity_Serialization_Handler  m_entity_serialize_handler;
        m_Entity_Deserialization_Handler m_entity_deserialize_handler;
    } Entity_Functions;

| Field | Type | Description |
|-------|------|-------------|
| `m_entity_dispose_handler` | `m_Entity_Handler` | Called when entity is released. **Required by core.** |
| `m_entity_update_handler` | `m_Entity_Handler` | Called each frame for entity logic. **Required by core.** |
| `m_entity_disable_handler` | `m_Entity_Handler` | Called when entity is disabled. **Required by core.** |
| `m_entity_enable_handler` | `m_Entity_Handler` | Called when entity is enabled. **Required by core.** |
| `m_entity_serialize_handler` | `m_Entity_Serialization_Handler` | Called for entity save. **Required by core.** |
| `m_entity_deserialize_handler` | `m_Entity_Deserialization_Handler` | Called for entity load. **Required by core.** |

### Handler Signatures

    typedef void (*m_Entity_Handler)(
            Entity *p_entity_self,
            Game *p_game,
            World *p_world);

    typedef PLATFORM_Write_File_Error (*m_Entity_Serialization_Handler)(
            Entity *p_entity_self,
            Game *p_game,
            PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
            World *p_world,
            Serialization_Request *p_serialization_request);

    typedef PLATFORM_Read_File_Error (*m_Entity_Deserialization_Handler)(
            Entity *p_entity_self,
            Game *p_game,
            PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
            World *p_world,
            Serialization_Request *p_serialization_request);

## Injection Mechanism

In `defines.h`:

    #include <types/implemented/entity_functions.h>
    #ifndef DEFINE_ENTITY_FUNCTIONS
    typedef struct Entity_Functions_t {
        m_Entity_Handler    m_entity_dispose_handler;
        m_Entity_Handler    m_entity_update_handler;
        ...
    } Entity_Functions;
    #endif

## Agentic Workflow

### Extension Pattern

Add game-specific function pointers after the required fields:

    typedef struct Entity_Functions_t {
        // Required by core:
        m_Entity_Handler    m_entity_dispose_handler;
        m_Entity_Handler    m_entity_update_handler;
        m_Entity_Handler    m_entity_disable_handler;
        m_Entity_Handler    m_entity_enable_handler;
        m_Entity_Serialization_Handler  m_entity_serialize_handler;
        m_Entity_Deserialization_Handler m_entity_deserialize_handler;
        // Game-specific:
        m_Entity_Handler    m_entity_attack_handler;
        m_Entity_Handler    m_entity_interact_handler;
    } Entity_Functions;

### Constraints

- **All fields MUST be function pointers** — undefined behavior will occur
  otherwise. The engine indexes into `Entity_Manager.entity_functions[]`
  by `Entity_Kind` and copies the entire struct.
- The six required handlers must not be removed or reordered.
- The `#define DEFINE_ENTITY_FUNCTIONS` line must not be removed.

## Header Guard

`IMPL_ENTITY_FUNCTIONS_H`
