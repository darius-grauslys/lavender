# Function Review: `register_game_action__input_for__client`

- **Function name:** `register_game_action__input_for__client`
- **File of origin:** `core/source/game_action/core/input/game_action__input.c`

## Semantic

Registers the game action logic entry for `Game_Action_Kind__Input` on the client side, configuring outbound/inbound flag sanitization masks and leaving both process handlers null. This entry governs how input game actions are sanitized when dispatched outbound (to be sent to the server) and when received inbound by the client.

## Pre-conditions

1. `p_game_action_logic_table` must be a valid, non-null pointer to an initialized `Game_Action_Logic_Table`.
2. The `Game_Action_Logic_Entry` for `Game_Action_Kind__Input` must already exist within the table (it is expected to be pre-allocated as part of the table's static array).

## Post-conditions

1. The `Game_Action_Logic_Entry` for `Game_Action_Kind__Input` is fully initialized with:
   - **Outbound flags:** `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE` (evaluates to `GAME_ACTION_FLAGS__NONE` / 0)
   - **Outbound mask:** `GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE` (evaluates to `GAME_ACTION_FLAGS__BIT_IS_ALLOCATED`)
   - **Inbound flags:** `GAME_ACTION_FLAGS__INBOUND_SANITIZE` (evaluates to `GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND`)
   - **Inbound mask:** `GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE` (evaluates to `GAME_ACTION_FLAGS__BIT_IS_ALLOCATED | GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND`)
   - **Process priority:** `PROCESS_PRIORITY__0_MAXIMUM` (0)
   - **Outbound process handler:** null (`0`)
   - **Inbound process handler:** null (`0`)
   - **Outbound/inbound process flags:** `PROCESS_FLAGS__NONE` (0)

## Correctness Verdict

Correct

## Semantic Alignment

The function correctly configures the client-side input game action logic entry. Key semantic decisions:

- **No `GAME_ACTION_FLAGS__BIT_IS_LOCAL` on outbound:** Unlike the server version (`register_game_action__input_for__server`), which sets `GAME_ACTION_FLAGS__BIT_IS_LOCAL` on outbound (meaning the server's processed input is not re-sent over TCP), the client version omits this flag. This is correct: the client's outbound input must be transmitted over TCP to reach the server. The `GAME_ACTION_FLAGS__BIT_IS_LOCAL` flag means "will not be sent over tcp," so its absence on the client side is intentional.

- **Null inbound process handler:** The client does not register an inbound process handler (`m_process__game_action__input__inbound_server` is replaced with null). This aligns with the design comment in the header: "client register only exists for relaying inputs to server" and "server drives client struct." The server processes input and updates the client's state through state synchronization, not through inbound input game actions.

- **Flag sanitization consistency:** The outbound/inbound flag masks and values follow the standard sanitization pattern used across all game action registrations (e.g., `initialize_game_action_logic_entry_as__message`, `initialize_game_action_logic_entry_as__react__out`). The outbound sanitize clears the `BIT_IS_ALLOCATED` flag, and the inbound sanitize clears `BIT_IS_ALLOCATED` while setting `BIT_IS_IN_OR__OUT_BOUND`.

## Implementation Correctness

- **Type compatibility:** All parameters match their expected types exactly. The first argument is `Game_Action_Logic_Entry *` (returned by `get_p_game_action_logic_entry_by__game_action_kind`), the flag arguments are `Game_Action_Flags` (uint8_t), the priority is `Process_Priority__u8` (uint8_t), the process handlers are `m_Process` (function pointer, with `0` for null), and the process flags are `Process_Flags__u8` (uint8_t). No implicit conversions or truncation occur.

- **Undefined behavior:** None. The function does not dereference `p_game_action_logic_table` directly — it delegates to `get_p_game_action_logic_entry_by__game_action_kind`, which is expected to handle the lookup. No pointer arithmetic, type punning, or out-of-bounds access occurs.

- **Validation:** Appropriate for the function's role as a registration function. It assumes the caller provides a valid table; validation of the table pointer is the caller's responsibility.

## Side Effects

Mutates the `Game_Action_Logic_Entry` for `Game_Action_Kind__Input` within the provided `Game_Action_Logic_Table`. All fields of the entry are overwritten: outbound/inbound flags, outbound/inbound masks, outbound/inbound process handlers, outbound/inbound process flags, and process priority.

## Related Observation: Bug in `initialize_game_action_for__input` (same file)

While reviewing the input game action module, a copy-paste bug was identified in the related function `initialize_game_action_for__input` (lines 84-96). In the `#ifdef SECURITY_0` code path, all three assignments after the first write to `input_flags__held` instead of their respective fields:

```c
p_game_action->ga_kind__input__input.input_flags__held =
    p_input->input_flags__held;       // correct field
p_game_action->ga_kind__input__input.input_flags__held =  // BUG: should be input_flags__pressed
    p_input->input_flags__pressed;
p_game_action->ga_kind__input__input.input_flags__held =  // BUG: should be input_flags__pressed_old
    p_input->input_flags__pressed_old;
p_game_action->ga_kind__input__input.input_flags__held =  // BUG: should be input_flags__released
    p_input->input_flags__released;
```

Lines 88, 90, and 92 all assign to `input_flags__held`, overwriting each other. The final value of `input_flags__held` would be `input_flags__released`, and the actual `pressed`, `pressed_old`, and `released` fields would remain at their default (zero) values. This causes semantic drift: when `SECURITY_0` is defined, only the held and released flags are correctly transmitted (released ends up in held's slot), while pressed and pressed_old are lost. This bug does not affect the function under review (`register_game_action__input_for__client`) but affects the overall input game action flow when `SECURITY_0` is enabled.
