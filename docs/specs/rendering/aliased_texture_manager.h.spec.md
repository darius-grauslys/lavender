# Specification: core/include/rendering/aliased_texture_manager.h

## Overview

Manages a pool of `Aliased_Texture` instances, providing allocation,
lookup (by name or UUID), and release of named textures. This is the
primary API for loading and accessing textures by human-readable names
at runtime.

## Dependencies

- `defines.h` (for `Aliased_Texture_Manager`, `Aliased_Texture`, `Texture`, `Texture_Flags`)
- `defines_weak.h` (forward declarations)

## Types

### Aliased_Texture_Manager (struct)

    typedef struct Aliased_Texture_Manager_t {
        Aliased_Texture aliased_textures[MAX_QUANTITY_OF__ALIASED_TEXTURES];
        Repeatable_Psuedo_Random repeatable_psuedo_random_for__texture_uuid;
    } Aliased_Texture_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `aliased_textures` | `Aliased_Texture[128]` | Fixed pool of aliased texture slots. |
| `repeatable_psuedo_random_for__texture_uuid` | `Repeatable_Psuedo_Random` | UUID generator for texture entries. |

### Constants

| Macro | Value | Description |
|-------|-------|-------------|
| `MAX_QUANTITY_OF__ALIASED_TEXTURES` | `128` | Maximum aliased textures. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_aliased_texture_manager` | `(Aliased_Texture_Manager*) -> void` | Initializes all aliased texture slots to empty. |

### Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_texture_with__alias` | `(PLATFORM_Gfx_Context*, PLATFORM_Graphics_Window*, Aliased_Texture_Manager*, Texture_Name__c_str, Texture_Flags, Texture*) -> bool` | `bool` | Allocates a new platform texture and registers it with the given alias. Returns `true` on **failure**, `false` on success. |
| `load_texture_from__path_with__alias` | `(PLATFORM_Gfx_Context*, PLATFORM_Graphics_Window*, Aliased_Texture_Manager*, Texture_Name__c_str, Texture_Flags, const char*, Texture*) -> bool` | `bool` | Loads a texture from a file path and registers it with the given alias. Returns `true` on **failure**, `false` on success. |

### Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_uuid_of__aliased_texture` | `(Aliased_Texture_Manager*, Texture_Name__c_str) -> Identifier__u32` | `Identifier__u32` | Returns the UUID of the aliased texture matching the given name. |
| `get_texture_by__alias` | `(Aliased_Texture_Manager*, Texture_Name__c_str, Texture*) -> bool` | `bool` | Looks up a texture by alias name. Returns `true` on **failure** (not found). |
| `get_texture_by__uuid` | `(Aliased_Texture_Manager*, Identifier__u32, Texture*) -> bool` | `bool` | Looks up a texture by UUID. Returns `true` on **failure** (not found). |

### Release

| Function | Signature | Description |
|----------|-----------|-------------|
| `release_all_aliased_textures` | `(PLATFORM_Gfx_Context*, Aliased_Texture_Manager*) -> void` | Releases all allocated textures and resets all slots. |
| `release_aliased_texture_by__alias` | `(PLATFORM_Gfx_Context*, Aliased_Texture_Manager*, Texture_Name__c_str) -> void` | Releases a texture by alias name. |
| `release_aliased_texture_by__uuid` | `(PLATFORM_Gfx_Context*, Aliased_Texture_Manager*, Identifier__u32) -> void` | Releases a texture by UUID. |

## Agentic Workflow

### Error Convention

Functions returning `bool` use **inverted convention**: `true` = failure,
`false` = success. This is consistent across the aliased texture API.

### Ownership

Owned by `Gfx_Context` (at `gfx_context.aliased_texture_manager`).
Individual entries are `Aliased_Texture` (see `aliased_texture.h`).
Registered at game init via `register_aliased_textures` (see
`implemented/aliased_texture_registrar.h`).

### Preconditions

- All functions require non-null pointers.
- `allocate_texture_with__alias`: repeated names will shadow textures in an
  unpredictable manner.
- You do NOT own the returned texture — the manager owns it.

## Header Guard

`ALIASED_TEXTURE_MANAGER_H`
