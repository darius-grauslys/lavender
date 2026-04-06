# 1. Animate Sprite Specification

## 1.1 File
`core/include/rendering/animate_sprite.h`

## 1.2 Purpose
**DEPRECATED / INACTIVE.** This header previously contained sprite animation
helpers but all function bodies are currently commented out. The animation
system has been refactored to use `Sprite_Animation` structs and
`m_Sprite_Animation_Handler` callbacks (see `sprite.h` and
`sprite_animation.h`).

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations |
| `defines.h` | `Sprite`, `Direction__u8` |
| `timer.h` | `Timer__u32` operations |

## 1.4 Status
All functions are commented out. This file is retained for reference only.
New code should use:
- `poll_sprite_for__animation` (from `sprite.h`)
- `set_sprite_animation` (from `sprite.h`)
- `Sprite_Animation` flag helpers (from `sprite_animation.h`)

## 1.5 Header Guard
`ANIMATE_SPRITE_H`
