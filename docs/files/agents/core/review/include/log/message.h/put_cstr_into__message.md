# put_cstr_into__message

**File of origin:** `core/source/log/message.c`

## Semantic

Appends a null-terminated C-string into the message body character by character by delegating to `put_char_into__message`. Returns `true` if the message body becomes full during the operation; returns `false` otherwise.

## Pre-conditions

1. `p_message` must be a valid, non-null pointer to an initialized `Message` struct. (In debug builds, a null `p_message` triggers `debug_abort`; in release builds, null dereference is undefined behavior.)
2. `cstr` must be a valid, non-null pointer to a null-terminated C-string. **The function does not validate `cstr` for null**, so passing null results in undefined behavior (null pointer dereference on `cstr[0]`).
3. The `Message` struct must have been previously initialized via `initialize_message` (or equivalent) so that `index_of__body`, `length_of__message__body`, and `message__body` are in a valid state.

## Post-conditions

1. All characters from `cstr` (up to the null terminator) are appended to `message__body`, up to `MESSAGE_MAX_LENGTH_OF` (96) characters. If the body fills before the entire string is consumed, remaining characters are silently discarded.
2. `index_of__body` is incremented for each character successfully written.
3. `length_of__message__body` is incremented for each character successfully written.
4. The return value is `true` if the body is full (i.e., `index_of__body >= MESSAGE_MAX_LENGTH_OF`), and `false` otherwise.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation does **not** fully fulfill the semantic intent stated in the header comment ("Returns true if message body is full"). When the input string has exactly `MESSAGE_MAX_LENGTH_OF` (96) characters, the following occurs:

- The loop iterates 96 times, calling `put_char_into__message` for each character. Each call writes to `message__body[0]` through `message__body[95]` and returns `false` (body not yet full at the start of each call).
- After the 96th character is written, `index_of__body` becomes 96 (body is now full).
- The loop then reads `cstr[96]`, which is the null terminator, causing the loop to exit normally.
- The function returns `false` — **but the body is full**.

This is a semantic mismatch: the function should return `true` when the body is full, but it returns `false` in this edge case. The function only returns `true` when `put_char_into__message` itself returns `true` (i.e., when the body was *already* full at the start of a call). It never detects the case where the body becomes full exactly at the last character of the string.

## Implementation Correctness

1. **Missing null check for `cstr`:** The function validates `p_message` in debug builds but never checks `cstr`. Dereferencing a null `cstr` causes undefined behavior. This is inconsistent with the debug-build validation pattern used for `p_message`.

2. **Incorrect return value on exact-fit strings:** As described in the Semantic Alignment section, when the input string length equals `MESSAGE_MAX_LENGTH_OF`, the function returns `false` despite the body being full. The final `return false` should instead be `return p_message->index_of__body >= MESSAGE_MAX_LENGTH_OF;` to correctly reflect the post-condition.

3. **Potential `Quantity__u8` overflow on `size_of__message`:** The loop counter `size_of__message` is typed as `Quantity__u8` (uint8_t, range 0–255). If `cstr` is longer than 255 characters, this variable will overflow and wrap around, potentially causing an infinite loop or out-of-bounds reads from `cstr`. In practice, `MESSAGE_MAX_LENGTH_OF` is 96, so the body fills up and the loop exits before overflow occurs. However, this is a latent bug: if `MESSAGE_MAX_LENGTH_OF` is ever increased beyond 255, this would break.

4. **No `const` correctness:** The `cstr` parameter is declared as `char *cstr` but is only read from, never written to. It should be `const char *cstr` for proper const-correctness. (This matches the codebase convention seen in `set_title_of__message`, which also uses non-const `char *`.)

5. **`put_char_into__message` does not validate `p_message`:** The callee `put_char_into__message` has no null check for `p_message`, but this is acceptable since `put_cstr_into__message` validates it before entering the loop.

## Side Effects

1. Mutates `p_message->message__body` by writing characters from `cstr` into the body buffer.
2. Mutates `p_message->index_of__body`, incrementing it by the number of characters successfully written.
3. Mutates `p_message->length_of__message__body`, incrementing it by the number of characters successfully written.
4. No I/O or other external side effects.
