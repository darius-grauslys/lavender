#ifndef IMPL_ENTITY_FUNCTIONS_H
#define IMPL_ENTITY_FUNCTIONS_H

#include "defines_weak.h"

#define DEFINE_ENTITY_FUNCTIONS

typedef struct Entity_Functions_t {
    /// 
    /// NOTE: Lavender will not compile if these definitions are missing.
    ///
    m_Entity_Handler    m_entity_dispose_handler;
    m_Entity_Handler    m_entity_update_handler;
    m_Entity_Serialization_Handler  m_entity_serialize_handler;
    m_Entity_Serialization_Handler  m_entity_deserialize_handler;

    ///
    /// Extend the struct here:
    ///

} Entity_Functions;

#endif
