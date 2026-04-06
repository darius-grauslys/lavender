# 1. Aliased Texture Specification

## 1.1 File
`core/include/rendering/aliased_texture.h`

## 1.2 Purpose
Provides operations on individual `Aliased_Texture` instances — textures
that are associated with a human-readable string name (alias). This is the
per-entry API; for pool management see `aliased_texture_manager.h`.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Aliased_Texture`, `Texture`, `Texture_Name__c_str` |

## 1.4 Types

### 1.4.1 `Aliased_Texture` (defined in `defines.h`)
