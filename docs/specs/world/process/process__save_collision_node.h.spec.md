# Specification: core/include/world/process/process__save_collision_node.h

## Overview

Declares the process handler for saving a collision node's data to disk.

## Dependencies

- `defines.h` (for `Process`, `Game`)

## Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_process__save_collision_node` | `(Process*, Game*) -> void` | Process handler (`m_Process` signature) that serializes a collision node to the filesystem. |

## Agentic Workflow

### Process Convention

This function follows the cooperative process model (see `process.h` spec).
The collision node to save is accessed via `p_process->p_process_data`.

### Usage

Dispatched by the global space serialization system. Not called directly
by game code.

## Header Guard

`PROCESS_SAVE_COLLISION_NODE_H`
