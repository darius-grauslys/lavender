# 1 Specification: core/include/world/process/process__save_collision_node.h

## 1.1 Overview

Declares the process handler for saving a collision node's data to disk.

## 1.2 Dependencies

- `defines.h` (for `Process`, `Game`)

## 1.3 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_process__save_collision_node` | `(Process*, Game*) -> void` | Process handler (`m_Process` signature) that serializes a collision node to the filesystem. |

## 1.4 Agentic Workflow

### 1.4.1 Process Convention

This function follows the cooperative process model (see `process.h` spec).
The collision node to save is accessed via `p_process->p_process_data`.

### 1.4.2 Usage

Dispatched by the global space serialization system. Not called directly
by game code.

## 1.5 Header Guard

`PROCESS_SAVE_COLLISION_NODE_H`
