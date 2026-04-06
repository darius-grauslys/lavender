# 1. Specification: core/include/rendering/font/font_manager.h

## 1.1 Overview

Manages a fixed-size pool of `Font` instances.

## 1.2 Dependencies

- `defines.h` (for `Font_Manager`, `Font`)

## 1.3 Types

### 1.3.1 Font_Manager (struct)

    typedef struct Font_Manager_t {
        Font fonts[MAX_QUANTITY_OF__FONT];
    } Font_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `fonts` | `Font[MAX_QUANTITY_OF__FONT]` | Fixed pool of font instances. |

### 1.3.2 Constants

| Macro | Value | Description |
|-------|-------|-------------|
| `MAX_QUANTITY_OF__FONT` | `8` | Maximum fonts in pool. |

## 1.4 Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_font_manager` | `(Font_Manager*) -> void` | `void` | Initializes all font slots as deallocated. |
| `allocate_font_from__font_manager` | `(Font_Manager*) -> Font*` | `Font*` | Allocates a font from the pool. Returns null if pool exhausted. |
| `release_font_from__font_manager` | `(Font_Manager*, Font*) -> void` | `void` | Returns a font to the pool. |

## 1.5 Agentic Workflow

### 1.5.1 Ownership

Owned by `Gfx_Context` (at `gfx_context.font_manager`). Accessed via
`get_p_font_manager_from__gfx_context`.

### 1.5.2 Preconditions

- All functions require non-null pointers.
- `release_font_from__font_manager`: font must belong to this manager.

## 1.6 Header Guard

`FONT_MANAGER_H`
