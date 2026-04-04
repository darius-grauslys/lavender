# System Overview: Global Space Game Actions (Chunk Lifecycle)

## Purpose

The global space game actions manage the lifecycle of chunks (global spaces)
through the game action system. Three actions cover the full cycle: requesting
a chunk to be loaded or generated, signaling that a chunk is resolved and
ready, and requesting that a chunk be serialized to persistent storage.

## Architecture

### Action Kinds

| Kind | Direction | Description |
|------|-----------|-------------|
| `Game_Action_Kind__Global_Space__Request` | Client → Server | Requests chunk load/generation at specified coordinates. |
| `Game_Action_Kind__Global_Space__Resolve` | Server → Client | Signals that a chunk is loaded and ready for use. |
| `Game_Action_Kind__Global_Space__Store` | Client → Server | Requests chunk serialization to disk. |

### Payload Summary

| Kind | Key Fields |
|------|------------|
| `Global_Space__Request` | `Global_Space_Vector__3i32` coordinates, `TCP_PAYLOAD_BITMAP` for chunk data fragments, `Timer__u32` timeout (default 4s). |
| `Global_Space__Resolve` | `Global_Space_Vector__3i32` coordinates. |
| `Global_Space__Store` | `Global_Space_Vector__3i32` coordinates. |

## Chunk Loading Flow

### Offline Mode

In offline mode, chunk loading is handled locally without network transfer:

    Local_Space_Manager
      |
      |-- (determines chunk needed)
      |
      v
    dispatch_game_action__global_space__request(p_game, chunk_coords)
      |
      |-- (process handler loads from disk or generates)
      |
      v
    dispatch_game_action__global_space__resolve(p_game, chunk_coords)
      |
      |-- (chunk is active and ready)

### Multiplayer Mode

In multiplayer mode, chunk data is transferred via `TCP_Delivery` fragments:

    Client                              Server
      |                                   |
      |-- Global_Space__Request --------->|
      |   (chunk_coords)                  |
      |                                   |-- (loads or generates chunk)
      |                                   |
      |<-- TCP_Delivery (index=0) --------|
      |<-- TCP_Delivery (index=1) --------|
      |<-- TCP_Delivery (index=...) ------|
      |                                   |
      |   (all fragments received)        |
      |   (chunk reassembled)             |
      |                                   |
      |<-- Global_Space__Resolve ---------|
      |   (chunk_coords)                  |
      |                                   |
      |   [Chunk active and ready]        |

### Fragment Tracking

The `Global_Space__Request` payload includes a `TCP_PAYLOAD_BITMAP` that
tracks which `TCP_Delivery` fragments have been received. The bitmap size
is determined by:

    TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Chunk)

### Timeout

The request carries a timeout (`GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT` = 4
seconds). If chunk data is not fully received within this window, the request
may be retried or abandoned.

## Chunk Storage Flow

When a chunk needs to be persisted (e.g. before unload or during save):

    1. Chunk is modified (CHUNK_FLAG__IS_UPDATED set).
    2. dispatch_game_action__global_space__store(p_game, chunk_coords).
    3. Process handler serializes chunk to disk via platform file system.
    4. CHUNK_FLAG__IS_UPDATED may be cleared after successful save.

## Registration

### Mode-Specific Registration

| Function | Mode |
|----------|------|
| `register_game_action__global_space__request_for__offline` | Offline |
| `register_game_action__global_space__request_for__client` | Client |
| `register_game_action__global_space__request_for__server` | Server |
| `register_game_action__global_space__resolve` | All modes |
| `register_game_action__global_space__store` | All modes |

The request action has mode-specific handlers because:
- **Offline**: Loads from disk or generates locally.
- **Client**: Sends request to server, receives fragments.
- **Server**: Loads/generates and sends fragments back to client.

The resolve and store actions use the same registration across all modes.

## Integration with Collision System

Once a chunk is resolved, its `Global_Space` is associated with a
`Collision_Node` in the `Collision_Node_Pool`. The resolve action signals
that the chunk is ready for:
- Rendering.
- Collision detection (hitboxes in the chunk's spatial region are tracked
  by the associated `Collision_Node`).
- Entity interaction.

## Preconditions and Postconditions

### Global_Space__Request

**Preconditions:**
- Chunk coordinates must be valid.

**Postconditions:**
- A chunk load/generation process is initiated.

### Global_Space__Resolve

**Preconditions:**
- A corresponding `Global_Space__Request` should have been issued.
- The chunk data must be fully loaded/generated.

**Postconditions:**
- The global space is marked as active and ready.

### Global_Space__Store

**Preconditions:**
- The chunk at the specified coordinates must be loaded and active.
- The chunk should have `CHUNK_FLAG__IS_UPDATED` set.

**Postconditions:**
- The chunk data is written to persistent storage.

## Error Handling

- If the chunk cannot be loaded or generated, the process handler may
  issue a `Bad_Request` back to the requesting client.
- If the timeout expires before all fragments are received, the request
  may be retried.
- If the platform file system fails during store, the process fails
  via `fail_process`.
