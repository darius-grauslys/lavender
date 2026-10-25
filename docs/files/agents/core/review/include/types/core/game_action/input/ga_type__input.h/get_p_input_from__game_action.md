get_p_input_from__game_action — core/include/types/core/game_action/input/ga_type__input.h

Retrieves a pointer to the Input payload within a Game_Action by skipping past the _Game_Action_Header via byte-level pointer arithmetic.

Pre-conditions:
1. p_game_action must be a non-null pointer to a valid Game_Action object.
2. The Game_Action must be of kind Game_Action_Kind__Input (or a compatible layout where the payload union contains a GA_Input__Payload). The function does not validate this; it is the caller's responsibility.

Post-conditions:
1. Returns a non-null pointer to the Input field within the GA_Input__Payload located immediately after the _Game_Action_Header portion of the Game_Action.
2. The returned pointer points into the internal memory of the Game_Action struct; no copy is made.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. The Game_Action struct begins with a union containing a struct identical in layout to _Game_Action_Header, followed by a payload union (_ga_payload_union). The function correctly uses sizeof(_Game_Action_Header) to compute the byte offset to skip past the header, then casts the resulting address to GA_Input__Payload* and accesses the input field. This matches the intended behavior of extracting the Input payload from a Game_Action of kind Input.

Implementation Correctness:
Type compatibility — p_game_action is cast to u8* for byte-level arithmetic, then to GA_Input__Payload* to access the input field. The return type is Input*, which matches the type of the input field. No implicit conversions or truncation occur.
Undefined behavior — No null dereference check is performed, but this is consistent with the codebase's pattern of using low-level inline accessors that assume valid input (see similar functions in game_action.h). The pointer arithmetic is well-defined: u8* arithmetic is byte-level and valid for any object pointer. The cast to GA_Input__Payload* is valid as long as the Game_Action's payload is of type GA_Input__Payload, which is the caller's responsibility.
Validation — No validation is performed within this function, which is appropriate for a low-level accessor. The caller is responsible for ensuring the Game_Action is of the correct kind and is non-null.

Side Effects:
No side effects. This is a pure accessor function that returns a pointer into the Game_Action's internal memory.
