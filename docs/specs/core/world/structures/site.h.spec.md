# 1 Specification: core/include/world/structures/site.h

## 1.1 Overview

Defines initialization for `Site` — a spatial grouping of structures within
a region. Sites have a bounding box and a pointer array of structures.

## 1.2 Dependencies

- `defines.h` (for `Site`, `Structure`, `Hitbox_AABB`)
- `defines_weak.h` (forward declarations)

## 1.3 Types

### 1.3.1 Site (struct)

    typedef struct Site_t {
        Serialization_Header _serialization_header;
        Site_Ptr_Array_Of__Structures ptr_array_of__structures_in__site;
        Hitbox_AABB bounding_box_of__site;
        Quantity__u8 quantity_of__structures_in__site;
    } Site;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for serialization. |
| `ptr_array_of__structures_in__site` | `Structure*[STRUCTURES_IN_SITE__MAX_QUANTITY_OF]` | Array of structure pointers. |
| `bounding_box_of__site` | `Hitbox_AABB` | Spatial bounds of the site. |
| `quantity_of__structures_in__site` | `Quantity__u8` | Number of structures. |

### 1.3.2 Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `SITE__WIDTH_IN__TILES` | `512` | Site width in tiles. |
| `SITE__HEIGHT_IN__TILES` | `512` | Site height in tiles. |
| `STRUCTURES_IN_SITE__MAX_QUANTITY_OF` | `STRUCTURE_MAX_QUANTITY_OF / 4` | Max structures per site. |
| `SITE_MAX_QUANTITY_OF` | `STRUCTURE_MAX_QUANTITY_OF / STRUCTURES_IN_SITE__MAX_QUANTITY_OF` | Max sites. |

## 1.4 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_site` | `(Site*) -> void` | Initializes to empty state. |

## 1.5 Header Guard

`SITE_H`
