# 1 Specification: core/include/collisions/implemented/hitbox_context/hitbox_manager_registrar.h

## 1.1 Overview

Provides the platform-implementable registration entry point for hitbox
manager types. This is an `implemented/` header, meaning its implementation
is provided by the game project (not by the engine core). It is called once
during game initialization to register all supported hitbox manager types
with the `Hitbox_Context`.

This is the bridge between the engine's generic hitbox abstraction and the
concrete hitbox manager implementations.

## 1.2 Dependencies

- `defines.h` (for `Hitbox_Context`)

## 1.3 Functions

### 1.3.1 Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_hitbox_managers` | `(Hitbox_Context*) -> void` | Registers all hitbox manager types by calling `register_hitbox_manager` for each supported type. Must be implemented by the game project. |

## 1.4 Agentic Workflow

### 1.4.1 Registration Sequence

This function is called once during game initialization, after
`initialize_hitbox_context` and before any hitbox managers are allocated:

    initialize_hitbox_context(&game.hitbox_context);
    register_hitbox_managers(&game.hitbox_context);
    // Now hitbox managers of registered types can be allocated.

### 1.4.2 Implementation Pattern

A typical implementation registers the AABB hitbox manager:

    void register_hitbox_managers(Hitbox_Context *p_hitbox_context) {
        register_hitbox_manager(
            p_hitbox_context,
            f_hitbox_manager__allocator_AABB,
            f_hitbox_manager__deallocator_AABB,
            f_hitbox_manager__opaque_property_access_of__hitbox_AABB,
            Hitbox_Manager_Type__AABB,
            QUANTITY_OF__HITBOX_COMPONENTS("width, height", 2),
            QUANTITY_OF__HITBOX_COMPONENTS("x, y, z", 3),
            SIZE_OF__HITBOX_COMPONENTS("u32", sizeof(u32)),
            SIZE_OF__HITBOX_COMPONENTS("i32F4", sizeof(i32F4)),
            SIZE_OF__HITBOX_COMPONENTS("i16F8", sizeof(i16F8)),
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS("none",
                FRACTIONAL_PERCISION_0__BIT_SIZE),
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS("4bit",
                FRACTIONAL_PERCISION_4__BIT_SIZE),
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS("8bit",
                FRACTIONAL_PERCISION_8__BIT_SIZE));
    }

Additional hitbox manager types (e.g. `Hitbox_Manager_Type__AAABBB`) can
be registered in the same function if implemented.

### 1.4.3 Preconditions

- `p_hitbox_context` must be non-null and previously initialized via
  `initialize_hitbox_context`.
- Must be called before any calls to
  `allocate_hitbox_manager_from__hitbox_context`.

### 1.4.4 Postconditions

- After `register_hitbox_managers`: All supported hitbox manager types have
  populated invocation table entries and registration records in the
  `Hitbox_Context`.

### 1.4.5 Error Handling

- If a type is registered twice, behavior depends on the
  `register_hitbox_manager` implementation (typically overwrites silently
  or calls `debug_warning`).
