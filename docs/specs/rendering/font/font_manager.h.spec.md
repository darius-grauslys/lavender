# Specification: core/include/rendering/font/font_manager.h

## Overview

Manages a fixed-size pool of `Font` instances.

## Dependencies

- `defines.h` (for `Font_Manager`, `Font`)

## Types

### Font_Manager (struct)

    typedef struct Font_Manager_t {
        Font fonts[MAX_QUANTITY_OF__FONT];
    } Font_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `fonts` | `Font[MAX_QUANTITY_OF__FONT]` | Fixed pool of font instances. |

### Constants

| Macro | Value | Description |
|-------|-------|-------------|
| `MAX_QUANTITY_OF__FONT` | `8` | Maximum fonts in pool. |

## Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_font_manager` | `(Font_Manager*) -> void` | `void` | Initializes all font slots as deallocated. |
| `allocate_font_from__font_manager` | `(Font_Manager*) -> Font*` | `Font*` | Allocates a font from the pool. Returns null if pool exhausted. |
| `release_font_from__font_manager` | `(Font_Manager*, Font*) -> void` | `void` | Returns a font to the pool. |

## Agentic Workflow

### Ownership

Owned by `Gfx_Context` (at `gfx_context.font_manager`). Accessed via
`get_p_font_manager_from__gfx_context`.

### Preconditions

- All functions require non-null pointers.
- `release_font_from__font_manager`: font must belong to this manager.

## Header Guard

`FONT_MANAGER_H`
