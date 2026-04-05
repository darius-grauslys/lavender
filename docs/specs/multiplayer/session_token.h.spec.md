# Specification: core/include/multiplayer/session_token.h

## Overview

Provides utility functions for `Session_Token` manipulation, specifically
the compression of 64-bit player UUIDs into 32-bit entity-compatible UUIDs.
Session tokens are the authentication primitive for multiplayer sessions,
linking a player's account identity to their in-game entity representation.

## Dependencies

- `defines.h` (for `Session_Token`, `Identifier__u32`, `Identifier__u64`)
- `defines_weak.h` (forward declarations)
- `numerics.h` (for `ARITHMETRIC_L_SHIFT`, `MASK`)
- `serialization/serialization_header.h` (for `BRAND_UUID`, `GET_UUID_BRANDING`)

## Types

### Session_Token (struct)

    typedef struct Session_Token_t {
        Identifier__u64 player_uuid;
        Identifier__u64 session_token;
    } Session_Token;

| Field | Type | Description |
|-------|------|-------------|
| `player_uuid` | `Identifier__u64` | Globally unique 64-bit player account identifier. |
| `session_token` | `Identifier__u64` | 64-bit session authentication token. Unique per session. |

The `Game` struct initializes its `session_token` field to
`{0, 0}` (both fields zero) at game initialization.

## Functions

### UUID Compression (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_uuid_u32_of__session_token_player_uuid_u64` | `(Session_Token) -> Identifier__u32` | `Identifier__u32` | Compresses the 64-bit `player_uuid` into a 32-bit UUID suitable for entity system use. The result is branded with `Lavender_Type__Player`. |

### Compression Algorithm

The 64-bit UUID is compressed to 32 bits by XOR-folding:

    1. Extract the upper half: ARITHMETRIC_L_SHIFT(MASK(31), 31) & player_uuid
       This selects bit 31 through bit 61 of the 64-bit value.
    2. Extract the lower half: MASK(31) & player_uuid
       This selects bits 0 through 30.
    3. XOR the two halves together.
    4. Brand the result with Lavender_Type__Player UUID branding via
       BRAND_UUID(uuid_u32, GET_UUID_BRANDING(Lavender_Type__Player, 0)).

The UUID branding system uses bits at `UUID_BRANDING__BIT_SHIFT__TYPE`
(bit 26) and `UUID_BRANDING__BIT_SHIFT__INDEX` (bit 20) to encode
type information into the UUID, allowing the engine to identify the
type of object a UUID refers to.

**Note:** Some bit information is lost in this compression. The server
is responsible for managing UUID collisions that may arise from the
64-to-32-bit reduction.

## Agentic Workflow

### Authentication Flow

Session tokens are used during the multiplayer connection handshake:

    [Client]
        → Populate Session_Token with player_uuid and session_token
        → Send via Game_Action_Kind__TCP_Connect__Begin
          (ga_kind__tcp_connect__begin__session_token field)

    [Server]
        → Receive Session_Token from Game_Action
        → Validate session_token
        → Compress player_uuid to u32 via
          get_uuid_u32_of__session_token_player_uuid_u64(...)
        → Use compressed UUID for entity allocation

### UUID Branding

The compressed UUID is branded with `Lavender_Type__Player` to
distinguish player entity UUIDs from other entity types in the
serialization system. This branding is applied via `BRAND_UUID`
and can be checked via `GET_UUID_BRANDING`.

### Preconditions

- The `Session_Token` must have a valid `player_uuid`. A zero
  `player_uuid` will produce a zero compressed UUID (before branding).

### Postconditions

- The returned `Identifier__u32` is branded with `Lavender_Type__Player`.
- The compression is deterministic: the same `player_uuid` always
  produces the same `Identifier__u32`.

### Collision Risk

The XOR-folding compression means that distinct 64-bit UUIDs can
map to the same 32-bit UUID. The server must detect and handle
such collisions during player entity allocation.
