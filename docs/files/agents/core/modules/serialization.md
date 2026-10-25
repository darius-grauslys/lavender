# Serialization — UUID Hashing, Headers, Pools, and Requests

**Sources:** `core/source/serialization/hashing.c` + `core/source/serialization/serialization_header.c` + `core/source/serialization/serialization_request.c` + `core/source/serialization/serialized_field.c` + `core/source/serialization/game_directory.c`

## Surface Concerns

The serialization system provides the identity layer for every entity, manager, and data structure in Lavender. A 32-bit UUID hashing scheme maps 32-bit random UUIDs to indices in fixed-capacity contiguous arrays with open-addressing collision resolution (a parallel 64-bit variant, `Serialization_Header__UUID_64`, covers the same ground). Layer: L1 (persistence/io). Called from every manager module for UUID-based lookup, allocation, and deallocation.

- **UUID generation** — `get_random__uuid_u32()` calls the PRNG, XORs with `IDENTIFIER__UNKNOWN__u32` to avoid the null sentinel, and returns a 32-bit value. Uses `Repeatable_Psuedo_Random` instances typically seeded with the low 32 bits of the owning manager's pointer address (process/entity/game-action managers), so UUID sequences are deterministic within a run.
- **Branding** — `GET_UUID_BRANDING(type, index)` creates a type/index mask; `BRAND_UUID` combines it with a raw UUID. Ensures different types (Game_Action, Process, Client, etc.) don't collide even if their raw UUIDs map to the same array index. `UUID_BRANDING__MASK`, `UUID_BRANDING__BIT_SHIFT__TYPE`, and `UUID_BRANDING__BIT_SHIFT__INDEX` are defined in `defines_weak.h`, alongside the `Lavender_Type` enum that supplies the type bits.
- **Binning and collision resolution** — `bound_uuid_to__contiguous_array()` computes `uuid % length`. `poll_for__uuid_collision()` performs linear probing from that index, wrapping around. It returns a valid index whenever the probe lands on a deallocated or matching slot, and `INDEX__UNKNOWN__u32` **only when the array is completely full** — callers detect the full case via `is_index_u32__out_of_bounds()`.
- **Lookup** — `dehash_identitier_u32_in__contigious_array()` finds the bin then walks the array for an exact UUID match. Returns NULL if not found. All managers call this via inline wrappers.
- **Contiguous array init** — `initialize_serialization_header__contiguous_array()` zeros every entry and sets UUID to `IDENTIFIER__UNKNOWN__u32`, placing all slots in deallocated state.
- **Serialized field linking** — `Serialized_Field` provides a weak reference mechanism: initialize with a UUID, then `link_serialized_field_against__contiguous_array()` resolves it. `is_p_serialized_field__linked()` verifies the data pointer and UUIDs match. Undefined behavior if the target struct does not have `Serialization_Header` as its first member.
- **Serialization request lifecycle** — `Serialization_Request` abstracts I/O for save/load. `activate_serialization_request()` handles file I/O or TCP multi-packet receive (with a heap-allocated bitmap tracking packet arrival). `deactivate_serialization_request()` frees resources and calls the platform release function. `PLATFORM_get_quantity_of__active_serialization_requests()` drives `run_game()`'s wait-out loop.
- **UUID derivation** — `merge_identifiers_u32(left, bits, right)` bitwise-merges two UUIDs: left keeps its top bits, right fills the remainder. Used for child UUIDs derived from parent UUIDs (e.g., chunks from global spaces).

## Public API Surface

### Key Types

**`Serialization_Header`** — defined in `defines.h`. Key members:
- `Identifier__u32 uuid` — 32-bit hash/UUID. `IDENTIFIER__UNKNOWN__u32` is the null/deallocated sentinel.
- `Quantity__u32 size_of__struct` — byte size of the containing struct (used for pointer arithmetic in array lookups).

**`Serialization_Header__UUID_64`** — same layout but with `Identifier__u64 uuid` for 64-bit UUID variants.

**`Serialization_Pool`** — defined in `defines.h`. Key members:
- `Serialization_Header *p_headers`
- `Quantity__u32 quantity_of__pool_elements`
- `Quantity__u32 size_of__element`

**`Serialization_Request`** — defined in `defines.h`. Key members:
- `void *p_file_handler` — platform file handle for file I/O.
- `void *p_data` — user data pointer (client or game action pointer).
- `void *p_tcp_packet_destination` — destination buffer for TCP multi-packet receive.
- `u8 *pM_packet_bitmap` — heap-allocated bitmap tracking received TCP packets.
- `Quantity__u16 quantity_of__bytes_in__destination` — total expected bytes.
- `Quantity__u16 quantity_of__tcp_packets__anticipated` — total expected packets.
- `serialization_request_flags` — flag set for allocation, activity, direction, and transport.

**`Serialized_Field`** — defined in `defines.h`. Key members:
- `void *p_serialized_field__data` — pointer to the resolved struct.
- `Identifier__u32 identifier_for__serialized_field` — UUID to resolve against.
- `Serialization_Header *p_serialized_field__serialization_header` — resolved header pointer.

### Key Functions

From `hashing.h`:
- `Index__u32 poll_for__uuid_collision(Serialization_Header *, Quantity__u32, Identifier__u32, Index__u32);` — returns a valid index for any probed slot (allocated or deallocated), `INDEX__UNKNOWN__u32` only when the array is full; callers check via `is_index_u32__out_of_bounds()`.
- `Identifier__u32 get_next_available__uuid_in__contiguous_array(Serialization_Header *, Quantity__u32, Identifier__u32);`
- `Serialization_Header *dehash_identitier_u32_in__contigious_array(Serialization_Header *, Quantity__u32, Identifier__u32);` — returns NULL if not found.
- `static inline Identifier__u32 get_next_available__random_uuid_in__contiguous_array(Serialization_Header *, Quantity__u32, Repeatable_Psuedo_Random *);`
- `static inline Serialization_Header *allocate_serialization_header_with__this_uuid(Serialization_Header *, Quantity__u32, Identifier__u32);`
- `static inline Serialization_Header *allocate_serialization_header(Serialization_Header *, Quantity__u32, Repeatable_Psuedo_Random *);`
- `static inline bool has_uuid_in__contiguous_array(Serialization_Header *, Quantity__u32, Identifier__u32);`
- `static inline Identifier__u32 bound_uuid_to__contiguous_array(Identifier__u32, Quantity__u32);`

From `serialization_header.h`:
- `void initialize_serialization_header(Serialization_Header *, Identifier__u32, Quantity__u32);`
- `void initialize_serialization_header__contiguous_array(Serialization_Header *, Quantity__u32, Quantity__u32);`
- `static inline void initialize_serialization_header_for__deallocated_struct(Serialization_Header *, Quantity__u32);`
- `static inline bool is_serialized_struct__deallocated(Serialization_Header *);`
- `static inline bool is_identifier_u32_matching__serialization_header(Identifier__u32, Serialization_Header *);`
- `Serialization_Header *get_p_serialization_header_from__contigious_array(Serialization_Header *, Quantity__u32, Index__u32);`

From `serialization_request.h`:
- `void initialize_serialization_request(Serialization_Request *);`
- `bool activate_serialization_request(Serialization_Request *, void *, Quantity__u16, bool);`
- `void deactivate_serialization_request(PLATFORM_File_System_Context *, Serialization_Request *);`
- `static inline void set_serialization_request_as__allocated/deallocated/active/inactive/read/write/keep_alive/fire_and_forget/tcp/io;`
- `static inline bool is_serialization_request__allocated/active/reading/writing/keep_alive/fire_and_forget/tcp_or_io;`

From `identifiers.h`:
- `static inline Identifier__u32 get_random__uuid_u32(Repeatable_Psuedo_Random *);`
- `static inline Identifier__u32 merge_identifiers_u32(Identifier__u32, Quantity__u8, Identifier__u32);`
- `static inline bool is_identifier_u32__invalid(Identifier__u32);`

From `serialized_field.h`:
- `void initialize_serialized_field(Serialized_Field *, void *, Identifier__u32);`
- `bool link_serialized_field_against__contiguous_array(Serialized_Field *, Serialization_Header *, Quantity__u32);`
- `void point_serialized_field_to__this_serialized_struct(Serialized_Field *, void *);`
- `static inline bool is_p_serialized_field__linked(Serialized_Field *);` — true only if the data pointer is set, its header UUID is valid, and both UUIDs match.
- `static inline` typed getters: `get_p_entity_from__serialized_field`, `get_p_inventory_from__serialized_field`, `get_p_chunk_from__serialized_field`.

From `serialization_pool.h`:
- `void initialize_serialization_pool(Serialization_Pool *, Quantity__u32, Quantity__u32);` — declared here (and used by `hash_map.h`), but **defined nowhere in core** (dangling).
- `Serialization_Header *allocate_from__serialization_pool(Serialization_Pool *);` — declared, no definition in core.
- `void release_from__serialization_pool(Serialization_Pool *, Serialization_Header *);` — declared, no definition in core.
- `static inline Serialization_Header *dehash_from__serialization_pool(Serialization_Pool *, Identifier__u32);` — note: passes `quantity_of__pool_elements * size_of__element` as the length argument (likely bug; the stride is already handled internally by the hashed lookup).
- `static inline void allocate_by_hash_in__serialization_pool(Serialization_Pool *, Identifier__u32);`

### Branding Macros (serialization_header.h)

- `GET_UUID_BRANDING(type, index)` / `BRAND_UUID(uuid, uuid__branding)` / `ALLOCATE_P(p_header, uuid)` / `DEALLOCATE_P(p_header)`
- `GET_UUID(p_header)` / `GET_UUID_P(p)` / `IS_DEALLOCATED(p_header)` / `IS_DEALLOCATED_P(p)`

## Known Rough Edges

- **`dehash_identitier_u32_in__contigious_array`** — load-bearing typos: "identitier" and "contigious". Must not be renamed without a project-wide rename.
- **`_serialiation_header`** in `Game_Action` / `_Game_Action_Header` — missing-'r' typo in the struct definitions in `defines.h`, not in `game_action.c`.
- **`SERIALZIATION_REQUEST_FLAG__IS_ALLOCATED` / `__IS_ACTIVE` / `__USE_SERIALIZER_OR_BUFFER`** — "SERIALZIATION" (extra 'I') in three of the six request flags; defined in `defines.h` and used in `serialization_request.h`.
- **`Repeatable_Psuedo_Random`** — "Psuedo" instead of "Pseudo". Used across many locations (the `get_pseudo_random_*` PRNG functions are spelled correctly).
- **`poll_for__uuid_collision`** returns a valid index for any probed slot (allocated or deallocated) and `INDEX__UNKNOWN__u32` only when the array is completely full — callers detect the full case with `is_index_u32__out_of_bounds()`.
- **`initialize_serialization_header_for__deallocated_struct`** takes no identifier parameter at all — it always writes `IDENTIFIER__UNKNOWN__u32`, so a deallocated init can never preserve a struct's previous UUID.
- **`get_p_serialization_header_from__contigious_array`** (typo: "contigious") uses `p_serialization_headers->size_of__struct` for stride — all entries in a contiguous array must share the same `size_of__struct`, or corrupted structs can cause out-of-bounds lookups.
- **`Serialization_Request` bitmap** — the only heap allocation in the serialization system, freed in `deactivate_serialization_request()`.
- **`save_game`** — declared in `game_directory.h` but defined nowhere in core (dangling declaration); the non-inline `serialization_pool.h` pool functions (`initialize_serialization_pool`, `allocate_from__serialization_pool`, `release_from__serialization_pool`) are dangling the same way.

## Key Files Table

| File | Role |
|------|------|
| `core/source/serialization/hashing.c` | UUID collision, lookup, allocation wrappers (random UUIDs come from `identifiers.h`) |
| `core/source/serialization/serialization_header.c` | Header init, contiguous array init, next-available scan |
| `core/source/serialization/serialization_request.c` | Request init, activate/deactivate, bitmap management |
| `core/source/serialization/serialized_field.c` | Field init, linking against arrays, struct point |
| `core/source/serialization/game_directory.c` | Game data path (`stat_game_data_file`), `append_path` |
| `core/include/serialization/hashing.h` | UUID allocation, lookup, random, branding functions |
| `core/include/serialization/identifiers.h` | UUID generation, merge, invalid checks |
| `core/include/serialization/serialization_header.h` | Branding macros, init/dealloc helpers (the header struct itself is in `defines.h`) |
| `core/include/serialization/serialization_pool.h` | Pool API — non-inline functions are dangling declarations; `dehash`/`allocate_by_hash` inlines |
| `core/include/serialization/serialization_request.h` | Request lifecycle API, flag setters/getters (the struct itself is in `defines.h`) |
| `core/include/serialization/serialized_field.h` | Field linking, typed getters (the struct itself is in `defines.h`) |
| `core/include/serialization/game_directory.h` | Game directory path functions; `save_game` declared but undefined |
