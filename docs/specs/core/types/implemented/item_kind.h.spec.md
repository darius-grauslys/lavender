# 1 Specification: core/include/types/implemented/item_kind.h

## 1.1 Overview

Template header that defines the `Item_Kind` enum — the set of item types
available in the game. This file is copied to the game project directory by
`tools/lav_new_project` and is meant to be extended by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_ITEM_KIND` is not defined after the
`#include`, `defines_weak.h` falls back to a built-in default.

## 1.3 Dependencies

None (self-contained).

## 1.4 Types

### 1.4.1 Item_Kind (enum)

    typedef enum Item_Kind {
        Item_Kind__None = 0,
        Item_Kind__Unknown
    } Item_Kind;

| Value | Description |
|-------|-------------|
| `Item_Kind__None` | No item / empty slot sentinel. |
| `Item_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## 1.5 Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/item_kind.h>
    #ifndef DEFINE_ITEM_KIND
    typedef enum Item_Kind { ... } Item_Kind;
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

    typedef enum Item_Kind {
        Item_Kind__None = 0,
        Item_Kind__Sword,
        Item_Kind__Shield,
        Item_Kind__Potion,
        Item_Kind__Unknown
    } Item_Kind;

### 1.6.2 Constraints

- `Item_Kind__None` must remain first (value 0).
- `Item_Kind__Unknown` must remain last.
- `Item_Kind__Unknown` is used for array sizing in
  `Item_Manager.item_templates[(u16)Item_Kind__Unknown]`.
- The `#define DEFINE_ITEM_KIND` line must not be removed.

## 1.7 Header Guard

`IMPL_ITEM_KIND_H`
