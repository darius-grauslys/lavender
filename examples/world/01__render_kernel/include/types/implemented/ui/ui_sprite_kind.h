#ifndef IMPL_UI_SPRITE_KIND_H
#define IMPL_UI_SPRITE_KIND_H

#define DEFINE_UI_SPRITE_KIND

typedef enum UI_Sprite_Kind {
    UI_Sprite_Kind__None = 0,
    UI_Sprite_Kind__8x8,
    UI_Sprite_Kind__16x16 
        = UI_Sprite_Kind__8x8,
    UI_Sprite_Kind__32x32 
        = UI_Sprite_Kind__16x16,
    UI_Sprite_Kind__Unknown = UI_Sprite_Kind__32x32
} UI_Sprite_Kind;

#endif
