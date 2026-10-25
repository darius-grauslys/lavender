#ifndef IMPL_TILE_KIND_H
#define IMPL_TILE_KIND_H

#define DEFINE_TILE_KIND

typedef enum Tile_Kind {
    Tile_Kind__None = 0,
    // GEN-NO-LOGIC-BEGIN
    // 1) Define tile kinds, matching 1:1 with their expected
    // tilesheet index slot.
    // Note, we define indices [1-2^N], 0 is reserved for transparent None.
    //
    // TUTORIAL NOTE (2.2 "logical tile layer resolutions"): each
    // layer is 4 bits, so a layer value is in [0..15]. That means
    // only tilesheet slots 1..15 are addressable from a layer —
    // exactly 15 kinds fit under the 4-bit ceiling, so we define
    // all 15 here (one per non-transparent slot).
    Tile_Kind__RED,        // 1
    Tile_Kind__BLUE,       // 2
    Tile_Kind__GREEN,      // 3
    Tile_Kind__YELLOW,     // 4
    Tile_Kind__CYAN,       // 5
    Tile_Kind__MAGENTA,    // 6
    Tile_Kind__ORANGE,     // 7
    Tile_Kind__PURPLE,     // 8
    Tile_Kind__WHITE,      // 9
    Tile_Kind__PINK,       // 10
    Tile_Kind__TEAL,       // 11
    Tile_Kind__OLIVE,      // 12
    Tile_Kind__BROWN,      // 13
    Tile_Kind__SILVER,     // 14
    Tile_Kind__GOLD,       // 15
    // GEN-NO-LOGIC-END

    Tile_Kind__Logical, /*Logical tiles can exceed tilesheet index limit*/
    // GEN-LOGIC-BEGIN
    // GEN-LOGIC-END
    Tile_Kind__Unknown
} Tile_Kind;

#endif
