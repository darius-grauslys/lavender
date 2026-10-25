PLATFORM_tcp_close_socket — core/include/platform.h (line 414)

Implementations reviewed:
- sdl/source/multiplayer/unix/sdl_unix_tcp_socket.c (26)
- sdl/source/multiplayer/win64/sdl_win64_tcp_socket.c (26)
- no_gui/source/multiplayer/no_gui_tcp_context.c (250)

## Semantic

Closes a PLATFORM_TCP_Socket's OS-level descriptor (close/closesocket) and resets
the socket struct to its inactive pool state. Returns true if any error was
encountered, false on success (per the header contract at platform.h:411-413:
"Returns true if the any errors were encountered."). The reset-to-inactive step
is Lavender-style pool cleanup (not RAII): it sets the socket handle to 0 so the
struct can be returned to a free pool.

## Pre-conditions

1. `p_PLATFORM_tcp_socket` must be non-null. (Only the NO_GUI implementation
   validates this; the SDL implementations dereference it unconditionally, which
   is undefined behavior if null.)
2. `p_PLATFORM_tcp_socket->socket_handle` must reference an open, owned socket
   descriptor.
3. The socket must not already have been closed/inactivated (no double-close
   guarantee is provided).
4. `p_PLATFORM_tcp_context` is declared but unused by all implementations; it is
   not required to be valid/initialized for this function.

## Post-conditions

1. On success the OS socket descriptor is released via close() (Unix) or
   closesocket() (Win64).
2. On success the socket struct is reset to inactive via the
   `_initialize_PLATFORM_tcp_socket_as__inactive` helper (sets socket_handle to 0).
3. Return value is true if any error occurred (null pointer in NO_GUI, or the
   underlying close failed); false if the socket was closed cleanly.
4. `p_PLATFORM_tcp_context` is never read or written (no observable effect).

## Correctness Verdict

Incorrect

## Semantic Alignment

The SDL (Unix) and SDL (Win64) implementations correctly fulfill the documented
intent: they return true on a close() failure and false on success, and they
reset the socket to inactive on the success path.

The NO_GUI implementation (`no_gui_tcp_context.c:250-265`) does NOT fulfill the
documented intent. Its return values are inverted relative to the header
contract:
- null `p_PLATFORM_tcp_socket` -> returns false (header contract: should be
  true, since this is an error).
- close() failure -> returns false (header contract: should be true).
- success -> returns true (header contract: should be false).

Its local doc comment ("Returns true if the socket was closed") describes true
= success, which matches the implementation but directly contradicts the header's
"Returns true if the any errors were encountered." This is a genuine
semantic/contract inversion, not a cosmetic issue.

## Implementation Correctness

- Type compatibility: parameter types match the header exactly (no implicit
  conversions or truncation). `socket_handle` access is type-correct.
- Undefined behavior:
  * SDL implementations perform no null check on `p_PLATFORM_tcp_socket`; a null
    argument would dereference null when reading `p_PLATFORM_tcp_socket->socket_handle`.
    NO_GUI guards against this. The inconsistency in defensive validation is a
    correctness gap for the SDL path.
  * No double-close protection exists on any path.
- The NO_GUI inversion is the primary defect. Under the header contract the
  return value is read by callers in a way that exposes the bug:
  `unbind_tcp_socket` (core/source/multiplayer/tcp_socket.c:177-183) treats the
  return value with true = success and false = failure (`if (!result) { ...failed
  to unbind... }`), which is the OPPOSITE of the header contract but matches the
  NO_GUI implementation. Consequently:
    * In a NO_GUI build, `unbind_tcp_socket` happens to work (it matches the
      inverted impl), but it contradicts the documented contract.
    * In an SDL build, `unbind_tcp_socket` would treat a successful close
      (SDL returns false) as a failure and skip clearing
      `p_tcp_socket->p_PLATFORM_tcp_socket`, and would treat a failed close
      (SDL returns true) as success and clear the pointer. So the SDL caller
      and the SDL implementation are mutually consistent with each other but
      both contradict the header contract and the core caller.
- Minor: the Win64 `PLATFORM_tcp_close_socket` failure-path debug_error message
  reads "SDL::WIN64::SDL_tcp_close_socket, failed to close socket." but it is
  logged inside `PLATFORM_tcp_close_socket` (sdl_win64_tcp_socket.c:30); the
  function-name label is wrong. Functionally harmless but misleading in logs.
- Validation appropriateness: null validation is present only in NO_GUI. For a
  function taking raw pointers to engine-internal structs, null validation is
  reasonable defensively, but consistency across all platform implementations is
  expected.

## Side Effects

- Releases the underlying OS socket descriptor (close/closesocket) — irreversible
  OS resource release.
- Resets the `PLATFORM_TCP_Socket` struct to its inactive initial state
  (socket_handle set to 0) on the success path, via the
  `_initialize_PLATFORM_tcp_socket_as__inactive` helper (Lavender-style pool
  cleanup so the struct can be reused/returned to a free pool).
- Emits a debug_error log message on the close-failure path.
- `p_PLATFORM_tcp_context` is not modified.
