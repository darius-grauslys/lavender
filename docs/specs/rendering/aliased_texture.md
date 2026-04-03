# Aliased Texture Specification

## File
`core/include/rendering/aliased_texture.h`

## Purpose
Provides operations on individual `Aliased_Texture` instances — textures
that are associated with a human-readable string name (alias). This is the
per-entry API; for pool management see `aliased_texture_manager.h`.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Aliased_Texture`, `Texture`, `Texture_Name__c_str` |

## Types

### `Aliased_Texture` (defined in `defines.h`)
