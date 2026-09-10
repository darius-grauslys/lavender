# AGENTS.md — harness_qa.py

`harness/harness_qa.py` is the agentic QA harness that launches a Lavender
binary and drives it through gdb (via `pygdbmi` / MI3). This file documents its
structure and the conventions contributors should follow.

## Quick look

```
python3 harness/harness_qa.py --program /path/to/lavender_game
```

The harness loads the binary into gdb and `-exec-run --start` so gdb 
owns the process and stops at `main`). After setup it enters a gdbmi read-loop 
so you can experiment interactively. Everything below the read-loop is skeleton 
(the langchain agent is not wired in yet).

## Architecture

| Piece | Role |
| --- | --- |
| `run_inside_gdb` | load + run under gdb to `main` |
| `main` | Orchestrates run, owns teardown, runs the read-loop |
| `GDBFrameController` | Base class: gdbmi handle + frame stack + low-level `_call`/`_exec`/`_eval` |
| `DebugInputDriver` | Helpers that invoke `drive_input.h` signatures |
| `DebugUIScannerExplorer` | Helpers that invoke `debug_ui.h` (`debug_get_ui_scanner`) |

### Frame management (`GDBFrameController`)
`push_frame(n)` saves the current gdb frame level and selects frame `n`;
`push_main_frame()` == `push_frame(0)`; `pop_frame()` restores the last saved
frame. Helpers wrap their work in `push_main_frame()`/`pop_frame()` so the
caller's frame context is always restored, even on error.

### Low-level gdb primitives
- `_call(expr)` — the CLI `call` via `-interpreter-exec console "call ..."`.
  **A `call`'s return value is NOT in the MI result payload** (it's only in a
  console stream record), so don't rely on it for return values.
- `_exec(stmt)` — arbitrary console statement, e.g. `set $x = ...`.
- `_eval(expr)` — `-data-evaluate-expression`; the reliable way to read a value
  back as JSON (`payload['value']`).

## Debug-input helpers (`DebugInputDriver`)
Mirror every signature in `core/include/debug/drive_input.h` (plus
`drop_input__flag` from `drive_input.c`, which isn't declared in the header but
is the natural companion to `debug_drive_input__flag`):

- `drive_input__flag(input_flag)` / `drop_input__flag(input_flag)`
- `drive_input__mouse_pos(x, y, z=0)`
- `dispatch_click(x, y, z=0)` → returns the spawned `Process *` address (parsed
  out of the `call` console stream, since `call` doesn't surface return values
  in the payload)

`input_flag` comes from the `Input_Flags__u32` IntEnum, a deliberate
DRY-violating mirror of the `INPUT_*` macros in
`core/include/platform_defaults.h` (`CLICK == 4096`, etc.) so the harness can
build bitmasks without parsing C headers. `Vector__3i32` args are passed as C
compound literals, e.g. `(Vector__3i32){10, 20, 5}` (a bare brace initializer
isn't valid as a C function argument).

## GDB navigation utilities (`gdb_nav_utils`)
`harness/gdb_nav_utils.py` provides high-level gdb navigation helpers that abstract
away raw MI3 command sequences. The first (and currently only) public API is:

### `step_frame(breakpoint_func: str, timeout: float = 5.0) -> bool`
Advances execution to a specific frame in the game loop, with infinite-loop
and breakpoint-storm protection.

Behavior:
1. Sets a temporary breakpoint at the given function (e.g.
   `manage_game__post_render`) using MI3 `-break-insert -t`.
2. Issues `continue` to run gdb **without reading any response** (`read_response=False`).
   This is critical: pygdbmi's `write()` with `read_response=True` can consume
   the `*stopped` (breakpoint-hit) notify record if it arrives within pygdbmi's
   0.2s additional-output-check window. On sequential frame steps (game loop
   already running), *running* and *stopped* can arrive in the same output chunk.
3. Polls for breakpoint-hit responses — `_poll_for_stops` is the sole consumer
   of gdb responses, correctly ignoring `*running` and other non-breakpoint-hit
   records.
4. If the hit is the expected breakpoint, returns `True`.
5. If a *different* breakpoint fires, continues running (tracking elapsed time
   against the timeout).
6. If the timeout expires before hitting the expected breakpoint, returns `False`
   — this catches:
   - **Infinite loops**: the expected frame never fires because the loop never
     returns.
   - **Breakpoint storms**: too many unexpected breakpoints firing, exhausting
     the time budget.

This abstracts the "step to end of frame" pattern where the game is run until
`manage_game__post_render` executes, ensuring the full scene loop has completed.

## Debug-ui helpers (`DebugUIScannerExplorer`)
Implements your "inspect UI via `debug_get_ui_scanner`" workflow:

```python
ex = DebugUIScannerExplorer(gdbmi)
ex.get_ui_scanner()                  # set $debug_ui_scanner = debug_get_ui_scanner(&game)
ex.read_field("p_ui_manager__current")
ex.read_fields()                     # all DEBUG_UI_Scanner fields -> dict
ex.next_element()                    # advance via m_next_element
ex.next_manager()                    # advance via m_next_manager
```

Things to know:
- `debug_get_ui_scanner` returns a `DEBUG_UI_Scanner` **by value**, so the
  scanner is captured by value into the convenience variable `$debug_ui_scanner`
  and fields are read with `.` member access (`...$debug_ui_scanner.field`).
- Fields are read with `-data-evaluate-expression` (via `_eval`), which puts the
  value in the JSON payload — unlike `call`, which buries it in a console record.
- gdb can't call a function pointer stored inside a convenience variable (error:
  *"Attempt to take address of value not located in memory"*). `next_element` /
  `next_manager` work around this by cast-and-call:
  `set $debug_ui_scanner = ((m_DEBUG_UI_Scanner_Func)$debug_ui_scanner.m_next_element)()`
- `debug_ui.h` is `#ifndef NDEBUG` guarded — the symbols are absent in release
  builds, so these calls will error at the gdb prompt in that case.
- `parse_hex("0x5555555551c3 <adv_element>")` → `"0x5555555551c3"`.

## Conventions for contributors
- Helpers are standalone (not wired into `main()`); instantiate them with a
  `GdbController` and call methods.
- Always wrap frame-dependent calls in `push_main_frame()`/`pop_frame()`.
- Prefer `-data-evaluate-expression` (`_eval`) for reading values; reserve
  `call` (`_call`) for side-effecting invocations where you don't need the
  return value.
- Mirror C enum/struct layouts by hand (DRY violation is intentional) rather
  than parsing headers, and keep the mirror commented with the C source.

## Verifying changes
```
python3 -m py_compile harness/gdb_nav_utils.py harness/verify_gdb_nav.py
python3 harness/verify_gdb_nav.py  # unit tests of response coordination (mock gdbmi)
python3 harness/verify_driver.py   # stub unit tests of frame stack + helpers
python3 harness/verify_sdl_lav.py  # integration test against real SDL2 binary
```

`verify_gdb_nav.py` tests the response-coordination fix (sequential
`step_frame` calls, batched `*running`+`*stopped` responses, `read_response=False`
usage) using a mock gdbmi controller. It does not require a display or a real
binary.

`verify_sdl_lav.py` launches the real `build/sdl/Lavender_Dev` executable
under gdb and exercises `step_frame()` against the live game loop.
It requires a display (`DISPLAY=:0`) for SDL2/GL initialization and sets it
automatically.
A real gdb + a binary mirroring the target header is the strongest check
(`verify_driver.py` asserts the exact gdb command strings; extend it when
adding signatures).
