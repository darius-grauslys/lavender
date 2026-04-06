# 1. Specification: core/include/rendering/animate_sprite.h

## 1.1 Overview

**DEPRECATED / INACTIVE.** This header previously contained sprite animation
helpers but all function bodies are currently commented out. The animation
system has been refactored to use `Sprite_Animation` structs and
`m_Sprite_Animation_Handler` callbacks.

## 1.2 Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Sprite`, `Direction__u8`)
- `timer.h` (for `Timer__u32` operations)

## 1.3 Types

None active.

## 1.4 Functions

None active. All functions are commented out.

## 1.5 Agentic Workflow

### 1.5.1 Status

This file is retained for reference only. New code should use:
- `poll_sprite_for__animation` (from `sprite.h`)
- `set_sprite_animation` (from `sprite.h`)
- `Sprite_Animation` flag helpers (from `sprite_animation.h`)

## 1.6 Header Guard

`ANIMATE_SPRITE_H`
