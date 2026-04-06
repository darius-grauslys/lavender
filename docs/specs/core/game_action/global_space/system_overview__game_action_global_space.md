# 1. System Overview: Global Space Game Actions (Chunk Lifecycle)

## 1.1. Purpose

The global space game actions manage the lifecycle of chunks (global spaces)
through the game action system. Three actions cover the full cycle: requesting
a chunk to be loaded or generated, signaling that a chunk is resolved and
ready, and requesting that a chunk be serialized to persistent storage.

## 1.2. Architecture

### 1.2.1. Action Kinds

| Kind | Direction | Description |
|------|-----------|-------------|
| `Game_Action_Kind__Global_Space__Request` | Client → Server | Requests chunk load/generation at specified coordinates. |
| `Game_Action_Kind__Global_Space__Resolve` | Server → Client | Signals that a chunk is loaded and ready for use. |
| `Game_Action_Kind__Global_Space__Store` | Client → Server | Requests chunk serialization to disk. |

### 1.2.2. Payload Summary

| Kind | Key Fields |
|------|------------|
| `Global_Space__Request` | `Global_Space_Vector__3i32` coordinates, `TCP_PAYLOAD_BITMAP` for chunk data fragments, `Timer__u32` timeout (default 4s). |
| `Global_Space__Resolve` | `Global_Space_Vector__3i32` coordinates. |
| `Global_Space__Store` | `Global_Space_Vector__3i32` coordinates. |

## 1.3. Chunk Loading Flow

### 1.3.1. Offline Mode

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

### 1.3.2. Multiplayer Mode

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

### 1.3.3. Fragment Tracking

The `Global_Space__Request` payload includes a `TCP_PAYLOAD_BITMAP` that
tracks which `TCP_Delivery` fragments have been received. The bitmap size
is determined by:

    TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Chunk)

### 1.3.4. Timeout

The request carries a timeout (`GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT` = 4
seconds). If chunk data is not fully received within this window, the request
may be retried or abandoned.

## 1.4. Chunk Storage Flow

When a chunk needs to be persisted (e.g. before unload or during save):

    1. Chunk is modified (CHUNK_FLAG__IS_UPDATED set).
    2. dispatch_game_action__global_space__store(p_game, chunk_coords).
    3. Process handler serializes chunk to disk via platform file system.
    4. CHUNK_FLAG__IS_UPDATED may be cleared after successful save.

## 1.5. Registration

### 1.5.1. Mode-Specific Registration

| Function | Mode |
|----------|------|
| `register_game_action__global_space__request_for__offline` | Offline |
| `register_game_action__global_space__request_for__client` | Client |
| `register_game_action__global_space__request_for__server` | Server |
| `register_game_action__global_space__resolve` | All modes |
| `register_game_action__global_space__store` | All modes |

The request action has mode-specific handlers because:
- **Offline**: Loads