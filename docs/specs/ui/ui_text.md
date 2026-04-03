# UI Text Specification

## File
`core/include/ui/ui_text.h`

## Purpose
Specializes a `UI_Element` as a read-only text display. Text elements render
a string using a `Font` and `Typer` for layout. The text buffer can be a
const string, a mutable owned string, or an internally allocated buffer.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `UI_Element`, `Typer`, `Font` |
| `defines_weak.h` | Forward declarations |

## Text-Specific Data (union members in `UI_Element`)
