# Debug — Severity-labeled output with platform hooks for coredump and abort

**Sources:** `core/source/debug/debug.c` + `core/include/debug/debug.h` + `core/include/debug/console.h`

## Surface Concerns

The debug module provides severity-labeled output functions that format messages with ANSI color codes via `printf` and route to platform hooks for coredump or abort behavior. All six functions are fully implemented in core with printf-based bodies in `debug.c` — despite the stale "NOT IMPLEMENTED BY CORE" comment in `debug.h`. The platform-specific behaviors (`PLATFORM_coredump`, `PLATFORM_pre_abort`, `PLATFORM_abort`) are declared in `platform.h` and implemented by each backend. Layer: SUPPORT (unlayered, used everywhere). This is the primary diagnostics path for the engine, called throughout core and game code.

- **Severity levels** — Five levels with distinct formatting: verbose (`(V) info:` white, `(V) warning:` yellow), info (`info:` black), warning (`warning:` yellow), error (`error:` red, then `PLATFORM_coredump()`), abort (`PLATFORM_pre_abort()`, then `abort:` red, then `PLATFORM_abort()`). Verbose is gated by `VERBOSE`; info/warning/error by `!NDEBUG`; all `printf` paths are additionally disabled by `NLOG`; the `debug_abort` hook calls are unguarded.
- **Backend delegation** — Three platform hooks, declared in `platform.h` and implemented by each backend (see [platform_api.md](../platform_api.md)): `PLATFORM_coredump` (called by `debug_error` after the message; execution continues if the hook returns), `PLATFORM_pre_abort` (called before the `abort:` message), `PLATFORM_abort` (called after the message; expected not to return).
- **Console helpers** — `print_console` and `clear_console` declared in `console.h` alongside an empty `Console` struct (placeholder). Declaration only: no implementation or call sites exist in core or any backend.
- **ANSI color codes** — All six messages `printf` ANSI color escapes; no code in the tree strips or rewrites them, so rendering depends on whatever stdout is attached to.

## Public API Surface

### Key Functions

- `void debug_info__verbose(const char *msg_fmt, ...);` / `void debug_warning__verbose(const char *msg_fmt, ...);` — White/yellow output prefixed `(V)`. Only when `VERBOSE` is defined (and `NLOG` is not); not gated by `NDEBUG`, so available in release builds.
- `void debug_info(const char *msg_fmt, ...);` — Black output prefixed `info:`. When `!NDEBUG` and `!NLOG`.
- `void debug_warning(const char *msg_fmt, ...);` — Yellow output prefixed `warning:`. When `!NDEBUG` and `!NLOG`.
- `void debug_error(const char *msg_fmt, ...);` — Red output prefixed `error:`, then `PLATFORM_coredump()`; execution continues if the hook returns. When `!NDEBUG` and `!NLOG`.
- `void debug_abort(const char *msg_fmt, ...);` — Calls `PLATFORM_pre_abort()`, prints red `abort:` prefixed message, calls `PLATFORM_abort()` (halts). Printf guarded by `!NDEBUG` and `!NLOG`; hook calls unguarded.
- `void print_console(const char *str);` / `void clear_console(void);` — Console helpers declared in `console.h`; no implementation in tree.

## Key Files Table

| File | Role |
|------|------|
| `core/source/debug/debug.c` | All six functions with ANSI formatting, platform hooks |
| `core/include/debug/debug.h` | API declarations + documentation |
| `core/include/debug/console.h` | Placeholder: empty Console struct, print/clear declarations |
