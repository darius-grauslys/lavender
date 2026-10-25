#ifndef IMPL_ENTITY_KIND_H
#define IMPL_ENTITY_KIND_H

#define DEFINE_ENTITY_KIND

typedef enum Entity_Kind {
    Entity_Kind__None = 0,
    // ***) Our first entity kind: a stationary "dummy" that just
    // draws a sprite.
    Entity_Kind__Dummy,
    Entity_Kind__Unknown
} Entity_Kind;

#endif
