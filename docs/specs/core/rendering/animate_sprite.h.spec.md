# Specification: core/include/rendering/animate_sprite.h

## Overview

**DEPRECATED / INACTIVE.** This header previously contained sprite animation
helpers but all function bodies are currently commented out. The animation
system has been refactored to use `Sprite_Animation` structs and
`m_Sprite_Animation_Handler` callbacks.

## Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Sprite`, `Direction__u8`)
- `timer.h` (for `Timer__u32` operations)

## Types

None active.

## Functions

None active. All functions are commented out.

## Agentic Workflow

### Status

This file is retained for reference only. New code should use:
- `poll_sprite_for__animation` (from `sprite.h`)
- `set_sprite_animation` (from `sprite.h`)
- `Sprite_Animation` flag helpers (from `sprite_animation.h`)

## Header Guard

`ANIMATE_SPRITE_H`
