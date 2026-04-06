# 1. Specification: core/include/game_action/core/global_space/game_action__global_space__request.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__Global_Space__Request` game action. This action
requests that a global space (chunk) at the specified coordinates be
loaded or generated.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`,
  `Global_Space_Vector__3i32`)
- `game.h` (for `dispatch_game_action_to__server`)

## 1.3. Game_Action_Kind

`Game_Action_Kind__Global_Space__Request`

## 1.4. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__global_space__request__gsv_3i32` | `Global_Space_Vector__3i32` | Chunk coordinates of the requested global space. |
| `ga_kind__global_space__request__chunk_payload_bitmap` | `TCP_PAYLOAD_BITMAP(Chunk, ...)` | Bitmap for tracking chunk data delivery fragments. |
| `ga_kind__global_space__request__timeout` | `Timer__u32` | Timeout in seconds (default: `GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT` = 4). |

## 1.5. Functions

### 1.5.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__global_space__request_for__client` | `(Game_Action_Logic_Table*) -> void` | Registers for client-side processing. |
| `register_game_action__global_space__request_for__server` | `(Game_Action_Logic_Table*) -> void` | Registers for server-side processing. |
| `register_game_action__global_space__request_for__offline` | `(Game_Action_Logic_Table*) -> void` | Registers for offline processing. |

### 1.5.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__global_space__request` | `(Game_Action*, Global_Space_Vector__3i32) -> void` | Initializes a global space request for the given chunk coordinates. |

### 1.5.3. Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__global_space__request` | `(Game*, Global_Space_Vector__3i32) -> bool` | `bool` | Dispatches a global space request to the server. |

## 1.6. Agentic Workflow

### 1.6.1. Chunk Loading Flow

1. The local space manager determines a chunk needs to be loaded.
2. `dispatch_game_action__global_space__request(p_game, chunk_coords)`.
3. **Offline**: The chunk is loaded from disk or generated locally.
4. **Multiplayer**: The server loads/generates the chunk and sends it
   back via `TCP_Delivery` fragments, tracked by the payload bitmap.

### 1.6.2. Timeout

The request has a 4-second timeout (`GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT`).
If the chunk data is not received within this window, the request may be
retried or abandoned.

### 1.6.3. Preconditions

- The chunk coordinates must be valid.

### 1.6.4. Postconditions

- A chunk load/generation process is initiated for the requested coordinates.
