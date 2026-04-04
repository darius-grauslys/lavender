# Specification: core/include/world/process/process__save_local_space_node.h

## Overview

Declares the process handler for saving a local space node's data to disk.

## Dependencies

- `defines.h` (for `Process`, `Game`)

## Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_process__save_local_space_node` | `(Process*, Game*) -> void` | Process handler (`m_Process` signature) that serializes a local space node to the filesystem. |

## Agentic Workflow

### Process Convention

This function follows the cooperative process model (see `process.h` spec).
The local space node to save is accessed via `p_process->p_process_data`.

### Usage

Dispatched by the world save system. Not called directly by game code.

## Header Guard

`PROCESS_SAVE_LOCAL_SPACE_NODE_H`
