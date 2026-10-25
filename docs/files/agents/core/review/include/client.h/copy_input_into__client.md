copy_input_into__client — core/include/client.h, lines 179-188

Copies an Input struct into a Client's inline input_of__client member via C struct assignment.

Pre-conditions:
1. p_client must be a non-null pointer to a writable Client object.
2. p_input must be a non-null pointer to a valid Input object to read from.
3. In debug builds (NDEBUG undefined), both pointers are guarded: if either is null the function returns immediately with no effect.
4. In release builds (NDEBUG defined), null checks are compiled out; the caller is responsible for ensuring both pointers are valid, otherwise undefined behavior occurs.

Post-conditions:
1. p_client->input_of__client is fully overwritten with a byte-for-byte copy of *p_input.
2. All Input members are replaced: input_flags__pressed, input_flags__held, input_flags__released, input_flags__pressed_old, cursor__3i32, cursor__old__3i32, writing_buffer (array), last_symbol, index_of__writing_buffer__read, index_of__writing_buffer__write, and input_mode__u8.

Correctness Verdict: Correct

Semantic Alignment:
The function faithfully implements the "copy input into client" intent. The C struct assignment p_client->input_of__client = *p_input performs a complete shallow copy of every member. The Input struct contains only primitive types and a fixed-size unsigned char array (writing_buffer) — no pointers, no nested owned resources. Therefore the shallow copy is semantically complete: no fields are omitted, no partial state remains, and no dangling pointers arise. No reordering of fields occurs relative to the Input struct definition (core/include/defines.h, line 1162). The assignment target is the inline Input member input_of__client (core/include/defines.h, line 2426), not a pointer-to-Input, so the copy is direct.

Implementation Correctness:
Type compatibility — p_client is Client *; p_client->input_of__client has type Input (an inline struct member, not a pointer); *p_input dereferences Input * to yield Input. The assignment is Input = Input — an exact type match. No implicit conversions or truncation occur.
No undefined behavior — in debug mode both pointers are null-checked before dereference, preventing null dereference. In release mode the null guard is compiled out, which is a deliberate, pervasive Lavender convention (observed across 100+ sites in the codebase). This means the contract is that callers must pass valid pointers in release builds.
No pointer arithmetic, no type punning, no out-of-bounds access. The writing_buffer array copy is performed by the struct assignment operator, which copies MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER bytes — bounded by the fixed-size array definition.
Validation — the debug-only null guard is appropriate for a low-level struct-copy utility. No additional validation is needed; this function's role is a mechanical field copy, and the caller bears responsibility for pointer validity in release builds.

Side Effects:
Mutates p_client->input_of__client — replaces all of its contents with a copy of *p_input. p_input is read-only (not modified). No memory allocation, no global or static state modification, no I/O.

Lavender-Specific Semantics:
This is not an initialization or reset function. The name "copy" indicates it overwrites existing state with the contents of another Input struct, rather than clearing to default initial conditions (Lavender-style pool cleanup) or performing resource setup (RAII). It does not touch p_client->client_flags__u16 or any other Client field — only input_of__client is mutated. It is neither Lavender-style initialization nor RAII resource acquisition.
