#ifndef HITBOX_KIND_H
#define HITBOX_KIND_H

#define DEFINE_HITBOX_KIND

typedef enum Hitbox_Kind {
    Hitbox_Kind__Opaque,
    Hitbox_Kind__AABB,
    // Hitbox_Kind__AAABBB,
    // Hitbox_Kind__Ball,
    // Hitbox_Kind__Sphere,
    Hitbox_Kind__Unknown
} Hitbox_Kind;

#endif
