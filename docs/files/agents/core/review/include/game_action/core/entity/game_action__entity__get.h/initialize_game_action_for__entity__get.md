initialize_game_action_for__entity__get — core/source/game_action/core/entity/game_action__entity__get.c

Initializes (resets) a Game_Action struct for an Entity__Get request, setting the action kind and the target entity UUID in the payload union.

Pre-conditions:
1. p_game_action must be a non-null pointer to a writable Game_Action struct.
2. uuid_of__target__u32 is any Identifier__u32 value; no range constraint is required.

Post-conditions:
1. The entire Game_Action struct is zeroed via initialize_game_action (Lavender-style initialization / pool cleanup, not RAII).
2. The serialization header is set to a deallocated state (IDENTIFIER__UNKNOWN__u32) via initialize_game_action.
3. The game action kind is set to Game_Action_Kind__Entity__Get.
4. The entity UUID field (uuid_of__entity__u32) in the GA_Entity__Payload union is set to uuid_of__target__u32.
5. The the_kind_of__entity field in the payload remains at 0 (Entity_Kind__None), which is the correct default for a "get" request since the entity kind is not known ahead of time — only the UUID is needed to look up the entity. This is consistent with the dispatch_game_action__entity__get inline helper, which also only takes a UUID.

Correctness Verdict: Correct

Semantic Alignment:
This function follows Lavender's initialization pattern (not RAII) — it resets the struct to zero via initialize_game_action and then sets specific fields. The function correctly sets the game action kind to Game_Action_Kind__Entity__Get and sets the entity UUID in the payload. The the_kind_of__entity field is intentionally left at 0 (Entity_Kind__None) because a "get" action only requires the UUID to look up the entity; the kind is determined by the server at lookup time. This is consistent with the sibling function initialize_game_action_for__entity__spawn, which does set the entity kind because a spawn action requires it. No struct fields are omitted or reordered — the GA_Entity__Payload has three fields (tcp_payload_bitmap, uuid_of__entity__u32, the_kind_of__entity), and the memset in initialize_game_action zeroes all of them, with the function then explicitly setting the uuid_of__entity__u32 field and leaving the others at their zeroed defaults.

Implementation Correctness:
Type compatibility — uuid_of__target__u32 is Identifier__u32 and the target field uuid_of__entity__u32 is also Identifier__u32; exact match, no implicit conversion or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (p_game_action validity is the caller's responsibility), no type punning, no out-of-bounds access. The payload is accessed via the GET_P_GAME_ACTION_PAYLOAD_AS_P macro which safely casts the union member.
Validation — no validation is needed for this low-level struct setup function; ensuring p_game_action is valid is the caller's responsibility.

Side Effects:
Mutates the Game_Action struct pointed to by p_game_action — the entire struct is zeroed via memset, then the serialization header, game action kind, and entity UUID fields are set.
