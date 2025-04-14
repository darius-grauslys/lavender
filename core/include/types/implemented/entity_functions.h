#ifndef IMPL_ENTITY_FUNCTIONS_H
#define IMPL_ENTITY_FUNCTIONS_H

#include "defines_weak.h"

#define DEFINE_ENTITY_FUNCTIONS

typedef struct Entity_Functions_t {
    m_Entity_Dispose_Handler        m_entity_dispose_handler;
} Entity_Functions;

#endif
