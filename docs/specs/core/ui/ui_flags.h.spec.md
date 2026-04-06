# 15 Specification: core/include/ui/ui_flags.h

## 15.1 Overview

Provides `static inline` helper functions for querying and mutating
`UI_Flags__u16` values. These flags describe the runtime state of a
`UI_Element` (allocated, enabled, held, dragged, focused, etc.).

**DEPRECATION NOTICE:** This file references flag bits
(`UI_FLAGS__BIT_IS_ALLOCATED`, `UI_FLAGS__BIT_IS_NEEDING_UPDATE`) that are
NOT defined in the current `defines.h`. The canonical flag operations now
live as `static inline` functions directly in `ui_element.h`. New code
should prefer the helpers in `ui_element.h`.

## 15.2 Dependencies

- `defines.h` (for `UI_Flags__u16` typedef and flag bit macros)

## 15.3 Types

### 15.3.1 UI_Flags__u16 (u16)

    typedef uint16_t UI_Flags__u16;

## 15.4 Functions

### 15.4.1 Query Functions (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_ui_flags__allocated` | `(UI_Flags__u16) -> bool` | `bool` | True if `UI_FLAGS__BIT_IS_ALLOCATED` is set. **WARNING:** flag not defined in current `defines.h`. |
| `is_ui_flags__enabled` | `(UI_Flags__u16) -> bool` | `bool` | True if `UI_FLAGS__BIT_IS_ENABLED` is set. |
| `is_ui_flags__needing_update` | `(UI_Flags__u16) -> bool` | `bool` | True if `UI_FLAGS__BIT_IS_NEEDING_UPDATE` is set. **WARNING:** flag not defined in current `defines.h`. |
| `is_ui_flags__being_held` | `(UI_Flags__u16) -> bool` | `bool` | True if `UI_FLAGS__BIT_IS_BEING_HELD` is set. |
| `is_ui_flags__being_dragged` | `(UI_Flags__u16) -> bool` | `bool` | True if `UI_FLAGS__BIT_IS_BEING_DRAGGED` is set. |
| `is_ui_flags__focused` | `(UI_Flags__u16) -> bool` | `bool` | True if the element is being held OR dragged. |

### 15.4.2 Mutation Functions (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_p_ui_flags__u8_as__allocated` | `(UI_Flags__u16*) -> void` | Sets `UI_FLAGS__BIT_IS_ALLOCATED`. |
| `set_p_ui_flags__u8_as__deallocated` | `(UI_Flags__u16*) -> void` | Clears `UI_FLAGS__BIT_IS_ALLOCATED`. |
| `set_p_ui_flags__u8_as__being_dragged` | `(UI_Flags__u16*) -> void` | Sets `UI_FLAGS__BIT_IS_BEING_DRAGGED`. |
| `set_p_ui_flags__u8_as__being_held` | `(UI_Flags__u16*) -> void` | Sets `UI_FLAGS__BIT_IS_BEING_HELD`. |
| `set_p_ui_flags__u8_as__dropped` | `(UI_Flags__u16*) -> void` | Clears both held and dragged flags. |
| `set_p_ui_flags__u8_as__enabled` | `(UI_Flags__u16*) -> void` | Sets `UI_FLAGS__BIT_IS_ENABLED`. |
| `set_p_ui_flags__u8_as__disabled` | `(UI_Flags__u16*) -> void` | Clears `UI_FLAGS__BIT_IS_ENABLED`. |

## 15.5 Agentic Workflow

### 15.5.1 Deprecation

This header references undefined flag bits and uses a naming convention
(`_u8`) inconsistent with the actual type (`UI_Flags__u16`). Prefer the
equivalent helpers in `ui_element.h` for new code.

## 15.6 Header Guard

`UI_FLAGS_H`
