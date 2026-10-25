clear_input — core/include/input/input.h

Resets the volatile input state (held/pressed/released flags and the active cursor) to defaults, preserving the current cursor as the previous-frame cursor before zeroing it.

Pre-conditions:
1. p_input must be a non-null pointer to a writable Input object. (No null check is performed; validating the pointer is the caller's responsibility, consistent with the low-level struct-assignment convention.)
2. input_flags__held, input_flags__pressed, input_flags__released are Input_Flags__u32 of any value.
3. cursor__3i32 holds the current cursor position as a Vector__3i32 of any value.
4. input_flags__pressed_old is intentionally NOT cleared here; SDL's PLATFORM_poll_input saves it before invoking clear_input, so it must be left untouched.

Post-conditions:
1. input_flags__held, input_flags__pressed, and input_flags__released are each set to INPUT_NONE (0).
2. cursor__old__3i32 holds the value cursor__3i32 had prior to the call (the previous-frame cursor position).
3. cursor__3i32 is reset to (0, 0, 0) by initialize_3i32_vector.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent. The name clear_input denotes resetting the volatile input state for reuse — this is Lavender-style initialization (cleaning up a struct to default conditions, NOT resource acquisition / RAII). It is invoked at the start of PLATFORM_poll_input (sdl_input.c:323, nds_input.c:16) precisely so the poll can repopulate the zeroed fields. The ordering is deliberate and correct: cursor__old__3i32 is copied from cursor__3i32 first, then cursor__3i32 is zeroed. Had the zeroing come first, cursor__old__3i32 would incorrectly be (0,0,0) and break click-drag detection (is_input__click_dragged compares cursor__3i32 against cursor__old__3i32). The flags that are persistent/stateful (input_flags__pressed_old, writing_buffer, last_symbol, buffer indices, input_mode__u8) are correctly left untouched, matching the test spec (test: clear_input__zeroes_all_flags_and_saves_cursor, referencing docs/specs/core/input/input.h.spec.md 1.4.4 Clear / 1.5.10 Postconditions).

Implementation Correctness:
Type compatibility — p_input->input_flags__held/pressed/released are Input_Flags__u32 (uint32_t) assigned INPUT_NONE (literal 0); no conversion/truncation. cursor__old__3i32 and cursor__3i32 are both Vector__3i32, so the assignment is a well-typed struct copy. initialize_3i32_vector takes Vector__3i32*, and &p_input->cursor__3i32 is exactly that.
Undefined behavior — none if p_input is non-null (the only assumption). No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The struct copy of Vector__3i32 (three i32 members) is a safe POD copy.
Validation — appropriate. This is a low-level inline reset; it deliberately performs no validation, leaving pointer responsibility to the caller, consistent with the codebase convention (cf. initialize_audio_effect).

Side Effects:
Mutates the Input struct pointed to by p_input: sets input_flags__held, input_flags__pressed, and input_flags__released to 0; copies cursor__3i32 into cursor__old__3i32; and zeroes cursor__3i32. No side effects beyond this single struct mutation.
