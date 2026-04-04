# Specification: core/include/rendering/aliased_texture.h

## Overview

Provides operations on individual `Aliased_Texture` instances — textures
that are associated with a human-readable string name (alias). This is the
per-entry API; for pool management see `aliased_texture_manager.h`.

## Dependencies

- `defines.h` (for `Aliased_Texture`, `Texture`, `Texture_Name__c_str`)

## Types

### Aliased_Texture (struct)

    typedef struct Aliased_Texture_t {
        Serialization_Header _serialization_header;
        Texture_Name__c_str name_of__texture__c_str;
        Texture texture;
    } Aliased_Texture;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for pool management. |
| `name_of__texture__c_str` | `char[MAX_LENGTH_OF__TEXTURE_NAME]` | Human-readable alias name. |
| `texture` | `Texture` | The wrapped texture. |

### Constants

| Macro | Value | Description |
|-------|-------|-------------|
| `MAX_LENGTH_OF__TEXTURE_NAME` | `32` | Maximum alias name length. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_aliased_texture` | `(Aliased_Texture*) -> void` | Initializes to empty state. **WARNING:** double-calling will leak memory if the texture was previously allocated. |

### Name Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_c_str_of__aliased_texture` | `(Aliased_Texture*, const char*) -> void` | `void` | Sets the alias name. Copies up to `MAX_LENGTH_OF__TEXTURE_NAME` bytes. |
| `is_c_str_matching__aliased_texture` | `(Aliased_Texture*, const char*) -> bool` | `bool` | True if the alias name matches the given string. |

### Texture Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `give_texture_to__aliased_texture` | `(Aliased_Texture*, Texture*) -> void` | `void` | Copies the `Texture` value into the aliased texture. Debug null-checked. |
| `get_texture_from__aliased_texture` | `(Aliased_Texture*) -> Texture` | `Texture` | Returns the `Texture` by value. Debug null-checked. |
| `is_aliased_texture__used` | `(Aliased_Texture*) -> bool` | `bool` | True if the alias name is non-empty (first byte is non-zero). Null-safe. |

## Agentic Workflow

### Ownership

Managed by `Aliased_Texture_Manager` (see `aliased_texture_manager.h`).
The `Texture` within is allocated via `PLATFORM_allocate_texture` or
`PLATFORM_allocate_texture_with__path`.

### Preconditions

- `give_texture_to__aliased_texture` and `get_texture_from__aliased_texture`
  require non-null `p_aliased_texture` in debug builds.
- `is_aliased_texture__used` is null-safe.

### Error Handling

- Debug builds call `debug_error` on null pointer violations.

## Header Guard

`ALIASED_TEXTURE_H`
