#ifndef IMPL_GRAPHICS_WINDOW_KIND_H
#define IMPL_GRAPHICS_WINDOW_KIND_H

#define DEFINE_GRAPHICS_WINDOW_KIND

typedef enum Graphics_Window_Kind {
    Graphics_Window_Kind__None = 0,
    // GEN-BEGIN
    // ***) Every UI window is also a Graphics_Window. Its "kind"
    // is what register_ui_window_into__ui_context / open_ui_window
    // key on, so give the HUD window its own enum value.
    Graphics_Window_Kind__UI__Hud,
    // GEN-END
    Graphics_Window_Kind__Unknown
} Graphics_Window_Kind;

#endif
