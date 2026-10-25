#ifndef IMPL_TILE_KIND_H
#define IMPL_TILE_KIND_H

#define DEFINE_TILE_KIND

typedef enum Tile_Kind {
    Tile_Kind__None = 0,
    // GEN-NO-LOGIC-BEGIN
    // 1) Define tile kinds, matching 1:1 with their expected
    // tilesheet index slot.
    // Note, we define indices [1-2^N], 0 is reserved for transparent None.
    Tile_Kind__RED,
    Tile_Kind__GREEN,
    // GEN-NO-LOGIC-END

    Tile_Kind__Logical, /*Logical tiles can exceed tilesheet index limit*/
    // GEN-LOGIC-BEGIN
    // GEN-LOGIC-END
    Tile_Kind__Unknown
} Tile_Kind;

#endif
