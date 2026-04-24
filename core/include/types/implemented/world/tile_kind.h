#ifndef IMPL_TILE_KIND_H
#define IMPL_TILE_KIND_H

#define DEFINE_TILE_KIND

typedef enum Tile_Kind {
    Tile_Kind__None = 0,
    // GEN-LOGIC-BEGIN
    // GEN-LOGIC-END
    Tile_Kind__Logical = Tile_Kind__None,

    // GEN-NO-LOGIC-BEGIN
    // GEN-NO-LOGIC-END
    Tile_Kind__Unknown
} Tile_Kind;

#endif
