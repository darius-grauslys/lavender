# 1. System Overview: Entity Game Actions (Spawn and Synchronization)

## 1.1. Purpose

The entity game actions handle entity creation and data synchronization
between client and server. Two actions cover these concerns: spawning a
new entity of a given kind, and requesting full entity data for an entity
the client does not have locally.

## 1.2. Architecture

### 1.2.1. Action Kinds

| Kind | Direction | Description |
|------|-----------|-------------|
| `Game_Action_Kind__Entity__Spawn` | Either (+ broadcast) | Requests creation of an entity with a specified kind and optional UUID. |
| `Game_Action_Kind__Entity__Get` | Client → Server | Requests entity data synchronization for a specific entity UUID. |

### 1.2.2. Payload Summary

| Kind | Key Fields |
|------|------------|
| `Entity__Spawn` | `Identifier__u32` entity UUID, `Entity_Kind` kind. |
| `Entity__Get` | `Identifier__u32` entity UUID, `TCP_PAYLOAD_BITMAP` for entity data fragments. |

## 1.3. Entity Spawn Flow

### 1.3.1. Targeted Spawn

A targeted spawn sends the request to the server for authoritative
processing:

    Client                              Server
      |                                   |
      |-- Entity__Spawn ----------------->|
      |   (uuid, Entity_Kind)            |
      |                                   |-- (allocates entity)
      |                                   |-- (initializes via f_entity_initializer)
      |                                   |

### 1.3.2. Broadcast Spawn

A broadcast spawn notifies all clients near a spatial point:

    Client / Server
      |
      |-- broadcast_game_action__entity__spawn(
      |       p_game, uuid, kind, broadcast_point)
      |
      |-- (sets IS_BROADCASTED flag)
      |-- (sets vector_3i32F4__broadcast_point)
      |
      v
    Server forwards to all clients near broadcast_point

Use `VECTOR__3i32F4__OUT_OF_BOUNDS` as the broadcast point for global
broadcast (all clients receive it regardless of position).

### 1.3.3. Registration

| Function | Mode |
|----------|------|
| `register_game_action__entity__spawn_for__server` | Server |
| `register_game_action__entity__spawn_for__client` | Client |

## 1.4. Entity Data Synchronization Flow

When a client needs full entity data it does not have locally:

    Client                              Server
      |                                   |
      |-- Entity__Get ------------------->|
      |   (entity uuid)                   |
      |                                   |-- (looks up entity)
      |                                   |
      |<-- TCP_Delivery (index=0) --------|
      |<-- TCP_Delivery (index=1) --------|
      |<-- TCP_Delivery (index=...) ------|
      |                                   |
      |   (all fragments received)        |
      |   (entity data reassembled)       |

### 1.4.1. Fragment Tracking

The `Entity__Get` payload includes a `TCP_PAYLOAD_BITMAP` that tracks
which `TCP_Delivery` fragments have been received:

    ga_kind__entity__get__entity_data_payload_bitmap

The bitmap size is determined by:

    TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Entity)

### 1.4.2. Registration

| Function | Mode |
|----------|------|
| `register_game_action__entity__get_for__server` | Server |
| `register_game_action__entity__get_for__client` | Client |

## 1.5. Integration with Entity Manager

The entity game actions interact with the `Entity_Manager` (see entity
module topology):

- **Spawn**: The server's process handler calls
  `allocate_entity_with__this_uuid_in__entity_manager` to create the
  entity, then invokes the `f_entity_initializer` registered on the
  `Entity_Manager`.
- **Get**: The server's process handler looks up the entity by UUID via
  `get_p_entity_by__uuid_from__entity_manager`, then serializes and
  sends the entity data via `TCP_Delivery` fragments.

## 1.6. Preconditions and Postconditions

### 1.6.1. Entity__Spawn

**Preconditions:**
- The entity kind must be valid (not `Entity_Kind__Unknown`).
- For broadcast, the broadcast point determines recipient clients.

**Postconditions:**
- The server creates the entity.
- In broadcast mode, all relevant clients are notified.

### 1.6.2. Entity__Get

**Preconditions:**
- The target UUID must be a valid entity UUID known to the server.

**Postconditions:**
- The server sends entity data back to the requesting client via
  `TCP_Delivery` fragments.

## 1.7. Error Handling

- If the entity UUID is unknown to the server, a `Bad_Request` may be
  dispatched back to the client.
- If the `Entity_Manager` pool is full during spawn, the process handler
  fails via `fail_process`.
- If `TCP_Delivery` fragments are lost or incomplete, the client's
  payload bitmap will not be fully set and the data cannot be reassembled.
