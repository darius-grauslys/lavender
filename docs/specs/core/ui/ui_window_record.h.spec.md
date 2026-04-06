# 17 Specification: core/include/ui/ui_window_record.h

## 17.1 Overview

Provides `static inline` query functions for `UI_Window_Record` — a
registration entry that describes how to load and close a UI window of a
given `Graphics_Window_Kind`, along with its resource requirements (sprite
count, UI element count).

## 17.2 Dependencies

- `defines.h` (for `UI_Window_Record` struct, `f_UI_Window__Load`, `f_UI_Window__Close`)

## 17.3 Types

### 17.3.1 UI_Window_Record (struct)

    typedef struct UI_Window_Record_t {
        f_UI_Window__Load f_ui_window__load;
        f_UI_Window__Close f_ui_window__close;
        Signed_Quantity__i32 signed_quantity_of__sprites;
        Signed_Quantity__i16 signed_quantity_of__ui_elements;
    } UI_Window_Record;

| Field | Type | Description |
|-------|------|-------------|
| `f_ui_window__load` | `f_UI_Window__Load` | Load callback. |
| `f_ui_window__close` | `f_UI_Window__Close` | Close callback. |
| `signed_quantity_of__sprites` | `Signed_Quantity__i32` | Sprite pool requirement. |
| `signed_quantity_of__ui_elements` | `Signed_Quantity__i16` | UI element count requirement. |

### 17.3.2 Callback Signatures

    typedef bool (*f_UI_Window__Load)(
            Gfx_Context *p_gfx_context,
            Graphics_Window *p_gfx_window,
            Game *p_game,
            UI_Manager *p_ui_manager,
            Index__u16 index_of__ui_element_offset__u16);

    typedef bool (*f_UI_Window__Close)(
            Gfx_Context *p_gfx_context,
            Graphics_Window *p_gfx_window,
            Game *p_game,
            UI_Manager *p_ui_manager);

### 17.3.3 Sprite Quantity Convention

| Value | Meaning |
|-------|---------|
| `> 0` | Allocate a new sprite pool of this size. |
| `< 0` | Use parent window's sprite pool. |
| `== 0` | No sprites needed. |

## 17.4 Functions (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_ui_window_record__valid` | `(UI_Window_Record*) -> bool` | `bool` | True if both `f_ui_window__load` and `f_ui_window__close` are non-null. |
| `is_ui_window_record__allocating_a_sprite_pool` | `(UI_Window_Record*) -> bool` | `bool` | True if `signed_quantity_of__sprites > 0`. |
| `is_ui_window_record__using_parent_sprite_pool` | `(UI_Window_Record*) -> bool` | `bool` | True if `signed_quantity_of__sprites < 0`. |

## 17.5 Agentic Workflow

### 17.5.1 Ownership

Stored in `UI_Context.ui_window_record[Graphics_Window_Kind__Unknown]`.
Registered via `register_ui_window_into__ui_context` (see `ui_context.h`).
Consulted by `open_ui_window_with__this_uuid_and__parent_uuid`.

## 17.6 Header Guard

`UI_WINDOW_RECORD_H`
