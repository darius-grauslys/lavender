#ifndef IMPL_UI_TILE_KIND_H
#define IMPL_UI_TILE_KIND_H

#define DEFINE_UI_TILE_KIND

#define UI_TILE_KIND__BIT_COUNT 10

typedef enum UI_Tile_Kind {
    UI_Tile_Kind__None,
    // GEN-BEGIN
    // ***) Like Tile_Kind, UI_Tile_Kind values map 1:1 onto the
    // window's tile map texture. Except the UI tile size is
    // 8px (UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT = 3), so index
    // N is the Nth 8x8px sub-tile of the 256x256 texture
    // (32x32 grid, row-major).
    // Our stock tileset's top-left 32px tile is solid red, so
    // 8px sub-tile 1 is an opaque red UI tile.
    UI_Tile_Kind__RED,
    // GEN-END
    UI_Tile_Kind__Unknown
} UI_Tile_Kind;

#endif


