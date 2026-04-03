# UI Flags Specification

## File
`core/include/ui/ui_flags.h`

## Purpose
Provides inline helper functions for querying and mutating `UI_Flags__u16`
values. These flags describe the runtime state of a `UI_Element` (allocated,
enabled, held, dragged, focused, etc.).

**DEPRECATION NOTICE:** This file references flag bits
(`UI_FLAGS__BIT_IS_ALLOCATED`, `UI_FLAGS__BIT_IS_NEEDING_UPDATE`) that are
NOT defined in the current `defines.h`. The canonical flag operations now
live as `static inline` functions directly in `ui_element.h`. New code
should prefer the helpers in `ui_element.h`.

## Dependencies
| Header       | Purpose                                      |
|--------------|----------------------------------------------|
| `defines.h`  | `UI_Flags__u16` typedef and flag bit macros   |

## Types

### `UI_Flags__u16` (defined in `defines.h`)
