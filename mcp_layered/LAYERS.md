# LAYERS.md — Layered Architecture of `mcp_layered/`

This document describes the stratified layering structure of `mcp_layered/`, a
refactored, hermit-crab shell-swap of `mcp/`. The existing `mcp/` code is
functional working code — the refactor replicates its semantics under a clean
layered architecture so that each concern is isolated, testable, and
composable.

## Layering Principle

Each layer **depends only on the layer directly below it**. Higher layers never
import or call lower layers directly except through the interface exposed by the
layer immediately beneath them. Each layer has a single, well-defined
responsibility.

```
┌────────────────────────────────────┐
│  6. layer_lav_mcp_server.py        │  MCP protocol adapter + session routing
├────────────────────────────────────┤
│  5. layer_lav_mcp.py               │  MCP protocol adaptation
├────────────────────────────────────┤
│  4. layer_lav_init.py              │  Initialization & default config
├────────────────────────────────────┤
│  3. layer_lav_cmd.py               │  Scanner drivers + Lavender commands
├────────────────────────────────────┤
│  2. layer_lav_config.py            │  Configuration
├────────────────────────────────────┤
│  1b. layer_pygdbmi.py              │  Dispatch layer (wraps pygdbmi)
│  1a. debug_response.py             │  GDB/MI response object model
├────────────────────────────────────┤
│  0. pygdbmi (external dependency)  │  Python interface to GDB/MI
└────────────────────────────────────┘
```

---

## Layer 0: `pygdbmi` (External Dependency)

**Package:** `pygdbmi`
**Role:** The Python interface to GDB's Machine Interface (MI) protocol.

`pygdbmi.GdbController` provides:
- `write(cmd: str)` — send an MI command to GDB.
- `get_gdb_response() -> list[dict]` — read the raw JSON response list.

This is the **only** external dependency and the lowest-level interface to GDB.
All higher layers operate through it.

---

## Layer 1a: `debug_response.py`

**File:** `mcp_layered/debug_response.py`
**Depends on:** Layer 0 (`pygdbmi` — only for type reference, not import)

**Role:** Represent a GDB/MI response as comprehensive Python objects.

`pygdbmi` returns a list of dictionaries. `debug_response.py` parses this JSON
output and builds a rich object model:

```python
class DebugResponse:
    """A single GDB/MI response record."""

class ResponseType(Enum):
    TARGET = "target"       # %..., @..., &..., ~...
    RESULT = "result"       # ^done, ^error, ^running, ^connected
    NOTIFY = "notify"       # *stopped, +=breakpoint-modified, etc.
    IMMEDIATE = "immediate" # raw prompt/output

class StoppedReason(Enum):
    BREAKPOINT_HIT = "breakpoint-hit"
    SIGNAL_RECEIVED = "signal-received"
    FUNCTION_DONE = "function-finished"
    WATCHPOINT_HIT = "watchpoint-triggered"
    SINGLE_STEP = "single-step"
    EXCEPTION = "exception-received"
    EXIT = "exited"
    EXIT_Q = "exited-normally"
    EXIT_SIG = "exited-signalled"
```

The module provides a `parse(response_list: list[dict]) -> DebugResponse` or
`parse_stream(response_list: list[dict]) -> list[DebugResponse]` function that
converts raw `pygdbmi` output into typed objects.

Each `DebugResponse` exposes:
- `type` — the `ResponseType`
- `reason` — the stop reason (for notify messages)
- `payload` — the full payload dict
- `bkpt_num` — breakpoint number if applicable
- `signal` — signal name if applicable
- `frame` — current frame info (pc, func, args, etc.)
- `threads` — thread list if applicable
- Convenience methods: `is_stopped()`, `is_error()`, `is_success()`, etc.

---

## Layer 1b: `layer_pygdbmi.py`

**File:** `mcp_layered/layer_pygdbmi.py`
**Depends on:** Layer 0 (`pygdbmi`), Layer 1a (`debug_response.py`)

**Role:** Abstract the dispatching process onto `pygdbmi`. Provides a
middleware/wrapper around `GdbController`.

This layer:
1. Wraps `pygdbmi.GdbController` in a class (e.g., `GDBSession`).
2. Uses `debug_response.py` to parse all responses from `pygdbmi`.
3. Holds a list of **hooks** (callables) that are invoked on every GDB response.
4. Hooks receive the parsed `DebugResponse` objects and can:
   - Inspect (e.g., detect breakpoint hits, signals)
   - Trigger side-effects (e.g., scan processes, log events)
   - Modify the response objects before they are returned to callers
5. Exposes a clean API:
   - `write(cmd: str) -> list[DebugResponse]` — send command, return parsed
   - `add_hook(hook_fn: Callable[[list[DebugResponse]], list[DebugResponse]])`
   - `remove_hook(hook_fn)`

This is the **single gateway** through which all GDB interaction occurs. All
higher layers interact with GDB through this layer's API.

---

## Layer 2: `layer_lav_config.py`

**File:** `mcp_layered/layer_lav_config.py`
**Depends on:** None (pure configuration/data layer)

**Role:** Configuration — where core dumps go, where screenshots go, where
logs go, what executable is run. Built to be extensible.

Provides:
- A `LavConfig` dataclass/class with:
  - `executable: str`
  - `core_dump_dir: str`
  - `screenshot_dir: str`
  - `log_file: str | None`
  - `gdb_path: str`
  - `gdb_args: list[str]`
  - `env: dict[str, str]`
  - Plus extensible fields for future scanners.
- `load_config(path: str | None) -> LavConfig` — load from a config file, with
  defaults for everything if the file is absent.
- `default_config() -> LavConfig` — returns a sensible default config.
- Exposes **required aliases** to config (e.g., `lav_config.executable`
  is accessible, `lav_config.dump_location` maps to `core_dump_dir`).

This layer does **not** import any other layer. It is pure configuration.

---

## Layer 3: `layer_lav_cmd.py`

**File:** `mcp_layered/layer_lav_cmd.py`
**Depends on:** Layer 1b (`layer_pygdbmi`), Layer 2 (`layer_lav_config`)

**Role:** Holds all Lavender Scanner drivers (e.g., `DebugUIScanner`,
`ProcessScanner`, etc.) and individual Lavender commands (e.g., `step`,
`start`, `ui_list`, `process_watch`).

This layer:
1. Imports scanner drivers and command implementations.
2. Exposes the config layer to these drivers.
3. Exposes **a required `alias` argument** to route to a scanner driver, then
   `**kwargs` to provide arguments to the scanner driver.
4. Scanner drivers can **reject** invocation on invalid kwargs — this raises an
   exception which propagates to Layer 5.
5. Example API:
   ```python
   def invoke(alias: str, gdb: GDBSession, config: LavConfig, **kwargs) -> str:
       """Route to scanner driver by alias."""
       driver = SCANNER_REGISTRY[alias]
       return driver.invoke(gdb, config, **kwargs)
   ```

This layer is the **command registry** — all actual work (stepping, scanning,
UI interaction, process tracking) lives here, implemented as scanner drivers.

---

## Layer 4: `layer_lav_init.py`

**File:** `mcp_layered/layer_lav_init.py`
**Depends on:** All layers below (1b, 2, 3)

**Role:** Initialization and wiring.

1. Accepts a `config_path: str | None` argument.
2. Forwards the path down to the config layer (Layer 2).
3. If no path is provided, uses `default_config()`.
4. Creates the `GDBSession` (Layer 1b) using config settings.
5. Returns a fully wired-up `LavSession` or similar facade that combines:
   - The `GDBSession` (Layer 1b)
   - The `LavConfig` (Layer 2)
   - The command router (Layer 3)

This layer is the **composition root** — it assembles all lower layers into a
working session.

---

## Layer 5: `layer_lav_mcp.py`

**File:** `mcp_layered/layer_lav_mcp.py`
**Depends on:** Layer 4 (`layer_lav_init`)

**Role:** Adapt the MCP protocol onto Layer 4.

This layer implements the MCP tool interface (tool discovery, tool calling) by
translating MCP tool names to Lavender scanner driver invocations through
`LavSession.invoke(alias, **kwargs)`.

It defines:
- The full MCP tool listing (`TOOLS` schema)
- A `dispatch_tool(name: str, arguments: dict) -> str` function
- Input validation and argument mapping

This layer **does not** know about GDB, pygdbmi, configs, or scanner drivers
directly — it only talks to `LavSession`.

---

## Layer 6: `layer_lav_mcp_server.py`

**File:** `mcp_layered/layer_lav_mcp_server.py`
**Depends on:** Layer 5 (`layer_lav_mcp`)

**Role:** Session tracking and session routing.

This is a **middleware** layer responsible for:
- Per-connection session management
- Session ID routing
- Forwarding config initialization to Layer 4 on session creation
- Managing the lifecycle of `LavSession` instances

It wraps the Layer 5 adapter in a session-aware envelope.

---

## Inspiration from `mcp/`

The existing `mcp/` code provides the semantics we are replicating:

| `mcp/` Concept | `mcp_layered/` Equivalent |
|---|---|
| `LavMcpSession` (single class) | Split across Layers 4+5 (`LavSession` + MCP adapter) |
| GDB interaction methods | Layer 1b (`GDBSession`) |
| Scanner drivers (`DebugUIScanner`, etc.) | Layer 3 (`layer_lav_cmd.py`) |
| Config fields in session | Layer 2 (`layer_lav_config.py`) |
| Response parsing (ad-hoc) | Layer 1a (`debug_response.py`) |
| Session factory/routing | Layer 6 (`layer_lav_mcp_server.py`) |

The key improvement is **isolation of concerns**: a change to GDB interaction
affects only Layer 1b; a change to a scanner driver affects only Layer 3; a
change to the MCP protocol affects only Layers 5–6.

---

## Future Extensions

- Layer 1b hooks enable **breakpoints-driven automation**: e.g., when GDB
  stops at `remove_process_from__process_table`, a hook triggers
  `DebugUIScanner.scan()` automatically.
- Layer 1b hooks enable **rich logging**: every breakpoint hit, signal, and
  error is logged with full context.
- Layer 2's extensibility allows new scanner drivers to add configuration
  fields without touching existing code.
