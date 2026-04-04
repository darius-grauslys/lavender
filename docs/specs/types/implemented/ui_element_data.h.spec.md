# Specification: core/include/types/implemented/ui_element_data.h

## Overview

Template header that defines the `UI_Element_Data` struct — the game-specific
data payload embedded in every `UI_Element`. This file is copied to the game
project directory by `tools/lav_new_project` and is meant to be extended by
the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_UI_ELEMENT_DATA` is not defined after
the `#include`, `defines.h` falls back to a built-in default (empty struct).

## Dependencies

- `defines_weak.h` (for forward declarations)

## Types

### UI_Element_Data (struct)

    typedef struct UI_Element_Data_t {

    } UI_Element_Data;

The default template is an empty struct. Games extend it with element-specific
fields.

## Injection Mechanism

In `defines.h`:

    #include <types/implemented/ui_element_data.h>
    #ifndef DEFINE_UI_ELEMENT_DATA
    typedef struct UI_Element_Data_t {
    } UI_Element_Data;
    #endif

## Agentic Workflow

### Extension Pattern

    typedef struct UI_Element_Data_t {
        void *p_custom_data;
        Identifier__u32 associated_entity_uuid;
    } UI_Element_Data;

### Constraints

- The struct is embedded in every `UI_Element` (at `ui_element.ui_element_data`),
  so its size affects the total `UI_Element` size and therefore the
  `UI_Manager` pool memory footprint.
- The `#define DEFINE_UI_ELEMENT_DATA` line must not be removed.

## Header Guard

`IMPL_UI_ELEMENT_DATA_H`
