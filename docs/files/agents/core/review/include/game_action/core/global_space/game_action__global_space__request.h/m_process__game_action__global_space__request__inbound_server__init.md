# m_process__game_action__global_space__request__inbound_server__init

**File of origin:** `core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c`

## Semantic

Initializes the inbound server process for a global space request by zeroing the TCP payload bitmap to its default state and binding the process run handler to `m_process__game_action__global_space__request__inbound_server`. This is a Lavender-style initialization (not RAII): it resets the payload bitmap to its initial conditions so the process is ready to receive inbound TCP chunk data.

## Pre-conditions

1. `p_this_process` must be non-null.
2. `p_this_process->p_process_data` must point to a valid, properly initialized `Game_Action` whose payload union contains a valid `GA_Global_Space__Request` structure.
3. `p_game` must be non-null (required by the `m_Process` function signature convention; not directly used by this function).

## Post-conditions

1. The `chunk_payload_bitmap` field within the `Game_Action`'s `GA_Global_Space__Request` payload is zeroed (all bits cleared).
2. `p_this_process->m_process_run__handler` is set to `m_process__game_action__global_space__request__inbound_server`, so subsequent process execution will invoke the inbound server handler.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills its semantic intent. The function resets the TCP payload bitmap to zero (its initial/clean state) and assigns the process run handler. This aligns with the Lavender convention where "init" means cleaning a struct to its initial conditions for reuse, not resource acquisition (RAII). No fields are omitted or reordered; the bitmap is fully cleared via `memset` with the correct size macro, and the handler is assigned atomically.

## Implementation Correctness

- **Type compatibility:** `get_p_tcp_payload_bitmap_u8_from__ga_global_space__request` returns `u8*`, which is implicitly convertible to `memset`'s `void*` first parameter. No truncation or conversion issues. `SIZE_OF__TCP_PAYLOAD_BITMAP__CHUNK` is defined as `sizeof(((Game_Action*)0)->_ga_payload_union.GA_Global_Space.GA_Global_Space__Request.chunk_payload_bitmap)`, which exactly matches the pointer returned by the getter. The handler assignment is type-correct: `m_process__game_action__global_space__request__inbound_server` has the signature `void(Process*, Game*)`, matching the `m_Process` typedef (`typedef void (*m_Process)(Process *p_this_process, Game *p_game)`) used for `m_process_run__handler`.
- **Undefined behavior:** No undefined behavior. No null pointer dereference (pointers are assumed valid per pre-conditions). No out-of-bounds access. The `memset` operates on a valid bitmap of the correct size.
- **Validation:** No pointer validation is performed (e.g., no null check on `p_this_process` or `p_game`). This is consistent with the codebase convention for `m_Process` functions — callers are expected to ensure valid pointers before invocation. The `p_game` parameter is unused by this function but is required by the `m_Process` signature convention.

## Side Effects

1. **Mutates** the `chunk_payload_bitmap` field within the `Game_Action` payload (zeroed via `memset`).
2. **Mutates** `p_this_process->m_process_run__handler` (set to the inbound server handler).
3. No other observable side effects. No memory allocation, no I/O, no global state modification.
