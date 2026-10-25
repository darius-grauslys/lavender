# Planning: client.h — Incorrect Modules

**Review source:** `agents/core/review/include/client.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/client.h`
- `core/source/client.c`
- `core/include/defines.h` (Client struct, lines 2421–2428)
- `core/include/defines_weak.h` (forward declarations, PLATFORM_Read_File_Error enum)
- `core/source/game.c` (callers: broadcast_game_action, m_game_action_handler__dispatch__*, m_game_action_handler__receive__*, dispatch_handler_process_to__load_client)
- `core/source/game_action/game_action_logic_table.c` (dispatch_game_action_process__inbound/outbound — confirm NULL dereference)
- `core/source/game_action/game_action_manager.c` (release_game_action_from__game_action_manager — confirms NULL write in release builds)
- `core/source/entity/entity.c` (reference: m_entity_deserialization_handler__default — correct `error = PLATFORM_read_file(...)` pattern)
- `core/include/game_action/game_action.h` (is_game_action__allocated, is_game_action__with_process, etc.)
- `core/include/game_action/game_action_logic_table.h` (dispatch_game_action_process__inbound/outbound declarations)
- `tests/core/source/test_suite_client.c` (empty — no tests exist for client)

---

## 1. Problem Identification

### 1.1 `is_client__failed_to_load` — `core/include/client.h`, lines 84–90

**Semantic drift** and **Boundary Condition** violation. The function name begins with `is_`, strongly implying a pure read-only **Predicate** (consistent with sibling `is_client__loaded`, `is_client__active`, `is_client__saving`, all of which are pure reads). However, `is_client__failed_to_load` mutates state by calling `set_client_as__inactive(p_client)` as its first statement. This violates **Information Hiding** — the caller cannot anticipate the side effect from the function name.

Compounding this, `set_client_as__inactive` (lines 78–82) has **no Precondition** guard for null `p_client`; it directly dereferences `p_client->client_flags__u16`. `is_client__failed_to_load` calls it unconditionally, so passing `NULL` triggers a null-pointer dereference. The `return p_client && ...` short-circuit in the return expression is a coincidence of evaluation order, not a safety guarantee — the UB occurs inside the callee call, which is reached before the short-circuit is evaluated.

### 1.2 `m_process__deserialize_client__default` — `core/source/client.c`, lines 405–467

**Translation Gap** in error handling. The `error` variable (line 436) is initialized to `PLATFORM_Read_File_Error__None` and is only ever reassigned to `0` inside the short-read block (line 454). The return value of `PLATFORM_read_file` (line 438) is **discarded** — never assigned to `error`. Consequently the `if (error)` check at line 457 is **dead code**: real I/O errors (`PLATFORM_Read_File_Error__System_Busy`, `PLATFORM_Read_File_Error__Unknown`) are silently swallowed, and the client is marked loaded even when the read failed, potentially with corrupted `Hitbox_AABB` data.

The correct pattern exists in `m_entity_deserialization_handler__default` (entity.c:331), which assigns `error = PLATFORM_read_file(...)` before checking `if (error)`.

### 1.3 `dispatch_game_action_for__client` — `core/source/client.c`, lines 292–403

**State Desync** / **Boundary Condition** — Bug #13. When a "with process" action is **already allocated** (`is_game_action__allocated(p_game_action)` is true), the local `p_game_action__allocated` (initialized to `0` at line 333) is never assigned `p_game_action`. It remains `NULL` and is then passed to:

1. `dispatch_game_action_process__outbound(...)` (line 341) — which calls `get_kind_of__game_action(p_game_action)` on `NULL` → null-pointer dereference.
2. `release_game_action_from__game_action_manager(...)` (lines 348–350) on process-failure — which writes a deallocated header through `NULL` in release builds.

The sibling `receive_game_action_for__client` has the identical defect.

### 1.4 `allocate_game_action_from__client` — `core/include/client.h`, line 49 (no implementation)

**Translation Gap** / **Stub-real divergence**. Declared in the public header with a well-formed signature but has **no implementation** anywhere in the project (confirmed absent from `core/source/client.c` and all backend sources). Any translation unit that calls it will produce a linker error. The `Game_Action_Manager` struct contains a 512-slot array; a correct implementation would scan for an empty slot, initialize it, and return the pointer.

### 1.5 `receive_game_action_for__client` — `core/source/client.c`, lines 182–289

**State Desync** / **Boundary Condition** — Bug #13 (same root cause as 1.3). In the `is_game_action__with_process` branch (lines 243–271), `p_game_action__allocated` is only assigned inside `if (!is_game_action__allocated(p_game_action))` (lines 246–256). When the action IS already allocated, `p_game_action__allocated` remains `NULL` and is passed to `dispatch_game_action_process__inbound(...)` (line 261) and `release_game_action_from__game_action_manager(...)` (line 267) — both dereference `NULL`.

Additional issues:
- **No Precondition** guard on `p_game_action` at entry — it is dereferenced unconditionally at line 195 via `get_kind_of__game_action(p_game_action)`. The sibling `dispatch_game_action_for__client` checks `p_game_action` for null at line 303; `receive` does not.
- **Surface-form leakage** in the comment at line 211: "responding game actions are --NEVER-- allocated a process." The code *does* process them inline (line 239 via `m_process_of__game_action`); the comment refers only to never dispatching to the process pool, but reads as contradictory to the code.

### 1.6 `set_entity_of__client` — `core/include/client.h`, lines 44–46 (no implementation)

**Translation Gap** / **Representation Invariant** violation — Bug #14. Declared but has **no implementation** anywhere in core or backends. Furthermore, the `Client` struct (`defines.h`, lines 2421–2428) has **no member capable of storing an `Entity *`** — it contains only `Serialization_Header`, two `Game_Action_Manager`s, `Local_Space_Manager`, `Input`, and `Client_Flags__u16`. Even if an implementation were added, there is no struct field to write to. This is a **dangling public declaration** that produces a linker error if called.

---

## 2. Impact Assessment

### 2.1 `is_client__failed_to_load`

- **Current callers:** None. The function is not invoked anywhere in `core/source/`, `nds/source/`, `sdl/source/`, or `tests/`. It is a `static inline` in a public header, so any future or external caller could invoke it.
- **Coupled code:** `set_client_as__inactive` (client.h:78) is only called by `is_client__failed_to_load`. `set_client_as__active` (client.h:96) does **not** call `set_client_as__inactive` — it directly manipulates flags, so fixing `is_client__failed_to_load` will not cascade to `set_client_as__active`.
- **Invalidated assumptions:** If any caller currently relies on the side-effect (clearing `CLIENT_FLAG__IS_ACTIVE`), removing the mutation will change behavior. The review indicates no such callers exist, so this is safe to correct.
- **De facto contract:** The `is_` naming convention across the header (`is_client__loaded`, `is_client__active`, `is_client__saving`) establishes an implicit **Representation Invariant** that `is_*` functions are pure predicates. `is_client__failed_to_load` violates this, and callers may have been written (or will be written) assuming purity.

### 2.2 `m_process__deserialize_client__default`

- **Current callers:** Registered as `p_game->m_process__deserialize_client` in `initialize_game` (game.c:138). Invoked via `dispatch_handler_process_to__load_client` (game.c:409) and `load_client` (game.c:484).
- **Coupled code:** `dispatch_handler_process_to__load_client` calls `set_client_as__failed_to_load(p_client)` (game.c:443) on process-init failure, but relies on `m_process__deserialize_client__default` to mark the client as failed-to-load on I/O errors during the process run. The dead `if (error)` block means this error path never fires.
- **Invalidated assumptions:** No callers currently depend on the broken behavior (swallowing errors), since the dead code path was never functional. Correcting it will cause real I/O errors to be logged and the client to be marked failed-to-load, which is the intended **Postcondition**.
- **Related:** `m_process__serialize_client__default` (client.c:469) correctly assigns `error = PLATFORM_write_file(...)` and checks it — this is the **Single Source of Truth (SSOT)** pattern that `deserialize` should follow.

### 2.3 `dispatch_game_action_for__client`

- **Current callers:**
  - `broadcast_game_action` (game.c:575, 606) — dispatches to local client and all remote clients in range.
  - `m_game_action_handler__dispatch__singleplayer` (game.c:761) — singleplayer dispatch path.
  - `m_game_action_handler__dispatch__multiplayer` (game.c:793) — multiplayer dispatch path.
  - All are routed through `Game::m_game_action_handler__dispatch` (game.h:356).
- **Coupled code:** `dispatch_game_action_process__outbound` (game_action_logic_table.c:45) and `release_game_action_from__game_action_manager` (game_action_manager.c:83) both dereference the `Game_Action *` argument. The bug only triggers when a "with process" action is **already allocated** — i.e., `is_game_action__allocated(p_game_action)` is true. In the current codebase, the `allocate_as__copy_of__game_action_from__game_action_manager` path (line 337) is the normal flow; the already-allocated path is the exception.
- **Invalidated assumptions:** No callers currently rely on the NULL-dereference behavior. Correcting it (assigning `p_game_action__allocated = p_game_action` in the already-allocated case) will make the already-allocated path functional. The `p_game_action = p_game_action__allocated` reassignment at line 337 in the non-allocated path will remain unchanged.
- **De facto contract:** The `if (!is_game_action__allocated(...))` guard demonstrates the code **anticipates** the already-allocated case, but the wiring is missing — a **Translation Gap** between intent and implementation.

### 2.4 `allocate_game_action_from__client`

- **Current callers:** None. Not invoked anywhere in the codebase.
- **Coupled code:** Paired API-wise with `release_game_action_from__client` (client.c:158), `dispatch_game_action_for__client`, and `receive_game_action_for__client`. The `Game_Action_Manager` struct and its inline helpers (`allocate_as__copy_of__game_action_from__game_action_manager`, `allocate_game_action_from__game_action_manager`) are fully implemented in `game_action_manager.h` — the infrastructure exists; only the `Client`-level wrapper is missing.
- **Invalidated assumptions:** Since the function is never called, no assumptions are coupled to its absence. Adding an implementation is purely additive.
- **De facto contract:** The function is declared in the public `client.h` header, implying it should be available. Its absence is a **Stub-real divergence** — the declaration passes structural/linking checks only if no translation unit references it.

### 2.5 `receive_game_action_for__client`

- **Current callers:**
  - `m_game_action_handler__receive__singleplayer` (game.c:804)
  - `m_game_action_handler__receive__multiplayer` (game.c:826)
  - Both are routed through `Game::m_game_action_handler__receive` (game.h:381), which is also called by `receive_game_action` (game.h:381) in `client__default.c` (nds backend, line 46).
- **Coupled code:** Same as 2.3 — `dispatch_game_action_process__inbound` (game_action_logic_table.c:69) and `release_game_action_from__game_action_manager` (game_action_manager.c:83) both dereference the `Game_Action *` argument.
- **Invalidated assumptions:** No callers rely on the NULL-dereference behavior. The missing null-check on `p_game_action` means a NULL argument crashes rather than returning `false` — callers in `m_game_action_handler__receive__multiplayer` (game.c:793) do check `p_client` for null but pass `p_game_action` through unconditionally.
- **De facto contract:** The `if (!is_game_action__allocated(...))` guard (line 246) demonstrates anticipation of the already-allocated case, but the wiring is missing — same **Translation Gap** as 2.3. The misleading comment at line 211 is **Surface-form leakage** that could mislead future maintainers.

### 2.6 `set_entity_of__client`

- **Current callers:** None. Not invoked anywhere in the codebase.
- **Coupled code:** The `Client` struct (`defines.h:2421-2428`) has no `Entity *` field. No other code references an entity binding on `Client`. The `Entity` type is forward-declared in `defines_weak.h` and fully defined in `defines.h:1127-1134`.
- **Invalidated assumptions:** No callers exist, so no assumptions are coupled.
- **De facto contract:** The declaration implies a binding relationship between `Client` and `Entity` that the struct does not support. This is a **Representation Invariant** violation — the struct cannot fulfill the declared contract.

---

## 3. Resolution Assessment

### 3.1 `is_client__failed_to_load` — `core/include/client.h`

**What needs to change:** Remove the `set_client_as__inactive(p_client)` side-effect call. The function should be a pure **Predicate** consistent with `is_client__loaded`, `is_client__active`, and `is_client__saving`. If the inactive-marking behavior is genuinely needed by a caller, it should be moved to the call site where the intent is explicit.

**Callers:** No callers currently exist. No caller updates needed.

**Tests/docs:** Add a `Property Based Testing` case verifying that calling `is_client__failed_to_load` does not alter `client_flags__u16`. Add a `Fuzzing` test for the null-input case to verify it returns `false` without crashing.

### 3.2 `m_process__deserialize_client__default` — `core/source/client.c`

**What needs to change:** Assign the return value of `PLATFORM_read_file` to `error`:

```c
error = PLATFORM_read_file(
        get_p_PLATFORM_file_system_context_from__game(p_game),
        (u8 *)p_hitbox_aabb,
        &length_of__read,
        1,
        p_serialization_request->p_file_handler);
```

This mirrors the correct pattern in `m_entity_deserialization_handler__default` (entity.c:331). The existing `error = 0` in the short-read block (line 454) correctly masks `End_Of_File` for the first-time-load case, while real system/busy errors that occur when `length_of__read == expected_length_of__read` will now be properly caught.

**Callers:** No caller changes needed. `dispatch_handler_process_to__load_client` (game.c:409) already handles process failure by calling `set_client_as__failed_to_load(p_client)` (game.c:443).

**Tests/docs:** Add a `Golden-file Test` that simulates a corrupted/truncated file read and verifies the client is marked `CLIENT_FLAG__IS_FAILED_TO_LOAD`. Add a `Round Trip Check` for the first-time-load path (no file → origin position → serialized → deserialized → origin position).

### 3.3 `dispatch_game_action_for__client` — `core/source/client.c`

**What needs to change:** After the `if (!is_game_action__allocated(p_game_action))` / `else` block, assign `p_game_action__allocated = p_game_action` so that the already-allocated case uses the original action pointer consistently:

```c
if (!is_game_action__allocated(p_game_action)) {
    p_game_action__allocated =
        allocate_as__copy_of__game_action_from__game_action_manager(...);
    if (!p_game_action__allocated) {
        ...
        return false;
    }
    p_game_action = p_game_action__allocated;
} else {
    p_game_action__allocated = p_game_action;  // <-- add this
}
```

Alternatively, place `p_game_action__allocated = p_game_action;` after the if/else block, before the dispatch call (line 341). This ensures `p_game_action__allocated` is never NULL when passed to `dispatch_game_action_process__outbound` and `release_game_action_from__game_action_manager`.

**Callers:** No caller changes needed. `broadcast_game_action` and the `m_game_action_handler__dispatch__*` functions pass already-allocated actions through this function; the fix makes the already-allocated path functional rather than crashing.

**Tests/docs:** Add a `Property Based Testing` case that dispatches an already-allocated "with process" action and verifies no crash occurs and the process is dispatched. Add a `Mutation Testing` case that mutates the already-allocated path to confirm the test catches the regression.

### 3.4 `allocate_game_action_from__client` — `core/include/client.h` / `core/source/client.c`

**What needs to change:** Implement the function in `core/source/client.c`. The implementation should delegate to the existing `allocate_game_action_from__game_action_manager` helper on `p_client->game_action_manager__outbound`:

```c
Game_Action *allocate_game_action_from__client(
        Client *p_client,
        Game_Action_Flags game_action_flags) {
    Game_Action *p_game_action =
        allocate_game_action_from__game_action_manager(
                get_p_game_action_manager__outbound_from__client(p_client));
    if (!p_game_action) {
        debug_error("allocate_game_action_from__client, failed to allocate p_game_action.");
        return 0;
    }
    initialize_game_action(p_game_action);
    p_game_action->game_action_flags = game_action_flags;
    return p_game_action;
}
```

Note: the `game_action_flags` parameter is currently unused by the inline helpers — the implementation should set the flags on the allocated action.

**Callers:** No callers currently exist. No caller updates needed.

**Tests/docs:** Add a `Property Based Testing` case that allocates from a client's outbound pool and verifies the returned action is non-null, allocated, and has the correct flags. Add a `Boundary Condition` test for pool exhaustion (all 512 slots allocated → returns NULL).

### 3.5 `receive_game_action_for__client` — `core/source/client.c`

**What needs to change:**

1. **NULL dereference fix (Bug #13):** Same as 3.3 — assign `p_game_action__allocated = p_game_action` in the already-allocated case (after the if/else block, before the dispatch call at line 261).

2. **Null-check on `p_game_action`:** Add a guard at entry (line 194), consistent with `dispatch_game_action_for__client` (line 303):
   ```c
   if (!p_game_action) {
       debug_error("receive_game_action_for__client, p_game_action is null.");
       return false;
   }
   ```

3. **Misleading comment (line 211):** Update "responding game actions are --NEVER-- allocated a process." to clarify that responding actions are never dispatched to the process *pool* but are still processed inline via `m_process_of__game_action`.

**Callers:** No caller changes needed. The fix makes the already-allocated path functional and prevents crashes on null input.

**Tests/docs:** Add a `Property Based Testing` case for the already-allocated "with process" path. Add a `Fuzzing` test for null `p_game_action` input. Add a `Round Trip Check` for the responding-action path (dispatch outbound → receive inbound → verify m_process ran).

### 3.6 `set_entity_of__client` — `core/include/client.h` / `core/include/defines.h`

**What needs to change:** This requires a two-part fix:

1. **Struct change:** Add an `Entity *p_entity` field to the `Client` struct in `defines.h` (lines 2421–2428):
   ```c
   typedef struct Client_t {
       Serialization_Header _serialization_header;
       Game_Action_Manager game_action_manager__inbound;
       Game_Action_Manager game_action_manager__outbound;
       Local_Space_Manager local_space_manager;
       Input input_of__client;
       Entity *p_entity;                    // <-- add
       Client_Flags__u16 client_flags__u16;
   } Client;
   ```

2. **Implementation:** Add the function body in `core/source/client.c`:
   ```c
   void set_entity_of__client(
           Client *p_client,
           Entity *p_entity) {
       if (!p_client) {
           debug_error("set_entity_of__client, p_client is null.");
           return;
       }
       p_client->p_entity = p_entity;
   }
   ```

**Callers:** No callers currently exist. No caller updates needed.

**Tests/docs:** Add a `Property Based Testing` case that sets an entity on a client and verifies the pointer is stored. Add a `Boundary Condition` test for null `p_client`.

**Phased approach:** The struct change in `defines.h` affects the `sizeof(Client)` and all serialization layout. Since `Client` is allocated via `malloc` and initialized via `initialize_client` (which uses `sizeof(Client)`), the change is backward-compatible at the allocation level but will change the serialized size. This should be coordinated with any existing save-file format. A phased approach is recommended: add the field first, then implement the function, then audit serialization code for size assumptions.

---

## 4. Test Verification Checklist

| Function | Existing Tests | Test Impact | New Tests Needed |
|---|---|---|---|
| `is_client__failed_to_load` | No — `test_suite_client.c` is empty (`#warning Please make tests for...`) | Low — no existing assertions to invalidate | `Property Based Testing` (predicate purity), `Fuzzing` (null input) |
| `m_process__deserialize_client__default` | No | Low — no existing tests | `Golden-file Test` (corrupted file → failed-to-load), `Round Trip Check` (origin position round-trip) |
| `dispatch_game_action_for__client` | No direct tests; callers in `game.c` are not unit-tested | Low — no existing assertions | `Property Based Testing` (already-allocated "with process" action), `Mutation Testing` |
| `allocate_game_action_from__client` | No | Low — no existing tests | `Property Based Testing` (allocation + flags), `Boundary Condition` (pool exhaustion) |
| `receive_game_action_for__client` | No | Low — no existing tests | `Property Based Testing` (already-allocated path), `Fuzzing` (null input), `Round Trip Check` (responding action) |
| `set_entity_of__client` | No | Low — no existing tests | `Property Based Testing` (pointer storage), `Boundary Condition` (null client) |

**Blast radius for tests:** Low. No existing tests assert on any of these functions' behavior. The `test_suite_client.c` file contains only an `#include <client.c>` and an empty `DEFINE_SUITE(client, END_TESTS)` with a `#warning` prompting test creation. New tests can be added without invalidating existing assertions.

---

## 5. Blast Radius Summary

- **Files requiring changes:** 3 source files + 1 header:
  - `core/include/client.h` — fix `is_client__failed_to_load` (remove side-effect), add `allocate_game_action_from__client` implementation declaration (already declared), fix `set_entity_of__client` declaration (already declared, needs implementation).
  - `core/source/client.c` — implement `allocate_game_action_from__client`, implement `set_entity_of__client`, fix `dispatch_game_action_for__client` (assign `p_game_action__allocated`), fix `receive_game_action_for__client` (assign `p_game_action__allocated`, add null check, fix comment), fix `m_process__deserialize_client__default` (assign `error = PLATFORM_read_file(...)`).
  - `core/include/defines.h` — add `Entity *p_entity` field to `Client` struct (3.6 only).
  - `tests/core/source/test_suite_client.c` — add test cases for all six functions.

- **Behavior preservation for current callers:**
  - `is_client__failed_to_load`: No callers exist. Removing the side-effect is safe.
  - `m_process__deserialize_client__default`: No callers depend on swallowed errors. The fix changes behavior only on actual I/O errors (which were previously silently ignored).
  - `dispatch_game_action_for__client` / `receive_game_action_for__client`: The fix only affects the already-allocated "with process" path, which currently crashes. No callers depend on the crash.
  - `allocate_game_action_from__client` / `set_entity_of__client`: No callers exist. Fixes are purely additive.

- **Phased approach needed:** The `set_entity_of__client` fix requires a struct layout change in `defines.h`, which affects `sizeof(Client)` and serialization. This should be done in coordination with save-file format considerations. The other five fixes are isolated and can be done independently.

- **De facto contracts invalidated:**
  - The `is_` prefix naming convention implies pure predicates — `is_client__failed_to_load` violates this.
  - The `if (!is_game_action__allocated(...))` guard in both `dispatch` and `receive` implies the already-allocated path is handled — it is not (Bug #13).
  - The `set_entity_of__client` declaration implies a `Client`→`Entity` binding exists — the struct has no such field (Bug #14).
