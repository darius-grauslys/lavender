"""Layer 5: MCP protocol adapter.

This layer adapts the MCP (Model Context Protocol) tool interface onto
Layer 4 (LavSession). It defines the full MCP tool listing schema and
a `dispatch_tool` function that maps MCP tool names to LavSession.invoke().

This layer does NOT know about GDB, configurations, or scanner drivers directly —
it only talks to LavSession.
"""

from __future__ import annotations

from typing import Any, Callable

from mcp_layered.layer_lav_init import LavSession
from mcp_layered.layer_lav_cmd import get_command_alias, CommandError


# -- MCP Tool Definitions (schema) -- #

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    # ---- session ----
    {
        "name": "session_start",
        "description": "Start the Lavender game under GDB if not already running.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "session_status",
        "description": (
            "Get the current session status: whether the game is running, "
            "halted, or crashed, plus the current backtrace."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "session_stop",
        "description": "Stop the Lavender game and exit the GDB session.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # ---- trace ----
    {
        "name": "trace",
        "description": (
            "Toggle trace BreakpointHooks. With no target, toggles the Process + "
            "Game_Action receive-marker hooks (ON by default: calling trace "
            "disables them, calling it again re-enables them). With target "
            "'ga'/'game_action'/'dispatch', toggles the deep Game_Action DISPATCH "
            "trace (OFF by default): on every dispatch it captures a callee "
            "backtrace + a client-scanner snapshot of the dispatched action/"
            "client, drained to the log at a safe point — a deep full trace of "
            "the engine, intentionally not fast. Other hooks (UI cache refresh "
            "and scene-transition tracking) are left unchanged."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": (
                        "Optional. Omit (or 'process') to toggle the Process + "
                        "receive-marker hooks (ON by default). Use 'ga', "
                        "'game_action', or 'dispatch' to toggle the deep "
                        "Game_Action dispatch trace (OFF by default)."
                    ),
                },
            },
            "required": [],
        },
    },
    # ---- navigate ----
    {
        "name": "navigate_step",
        "description": (
            "Advance one or more game frames: continue to manage_game__post_render, "
            "then execute 'finish' to reach the post-render state. "
            "Repeats count times (default 1). The step is guarded by a frame-"
            "heartbeat watchdog (default 30s, see timeout): as long as the game "
            "keeps crossing frame boundaries it never times out, however long "
            "individual frames take; a game stuck inside one frame (e.g. in an "
            "infinite non-fatal debug_error retry loop) is detected and the step "
            "returns a bounded timeout result carrying the captured debug_error "
            "reports. Since -DCRASH_ON_ERROR is off, non-fatal debug_errors are "
            "surfaced in the response in the same shape the old crash report "
            "had (backtrace + arguments + error message); the game keeps "
            "running."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of frames to step (default 1, must be >= 1).",
                    "default": 1,
                },
                "timeout": {
                    "type": "number",
                    "description": (
                        "Watchdog in seconds: max time allowed WITHOUT the game "
                        "crossing a frame boundary (default 30). 0 — or any "
                        "negative value, e.g. -1 — disables it (unbounded step)."
                    ),
                    "default": 30.0,
                },
            },
            "required": [],
        },
    },
    {
        "name": "navigate_source",
        "description": "Print the current backtrace and the source of the current frame.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # ---- core ----
    {
        "name": "core_dump",
        "description": "Extract a core dump of the current game state to disk.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "core_load",
        "description": "Stop the game and load a previously saved core dump by UUID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "uuid": {
                    "type": "string",
                    "description": "UUID of the core dump to load (from core_dump).",
                }
            },
            "required": ["uuid"],
        },
    },
    {
        "name": "core_reset",
        "description": "Stop the game and reload the last core dump loaded via core_load.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # ---- process ----
    {
        "name": "process_list",
        "description": "List all processes currently managed by the game's Process_Manager.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "process_watch",
        "description": (
            "Set a breakpoint on the specified process's function handler and "
            "continue until it is hit. Returns when the process is in frame."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "process_ptr": {
                    "type": "string",
                    "description": "Hex pointer to the Process to watch (from process_list).",
                }
            },
            "required": ["process_ptr"],
        },
    },
    {
        "name": "process_handler",
        "description": (
            "Resolve a process's run-handler function name from its pointer, at a "
            "safe (halted) point. The handler is bound AFTER creation, so call this "
            "while the process is running to learn WHICH handler a process uses — "
            "e.g. to identify what handler caused a debug_error for a ptr seen in "
            "the process trace. The result is logged to the session log (event=handler, "
            "keyed by the process pointer)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "process_ptr": {
                    "type": "string",
                    "description": (
                        "Hex pointer to the Process (from a create/remove/error "
                        "process-trace record, or process_list)."
                    ),
                }
            },
                "required": ["process_ptr"],
        },
    },
    {
        "name": "process_pool",
        "description": (
            "Snapshot the game's process pool while the game is HALTED: how many "
            "of the 512 pool slots are occupied and by WHICH run-handlers (and "
            "Process_Kind). Drives the C DEBUG_Process_Scanner to enumerate the "
            "active processes. Use this to diagnose a pool SATURATION (capacity) "
            "vs. a specific handler over-accumulating (leak) — e.g. after a step "
            "that timed out in a stuck frame. Returns the active/free counts, a "
            "saturated flag, and per-handler / per-kind tallies."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_iter": {
                    "type": "integer",
                    "description": (
                        "Max pool slots to walk before stopping (default 512, the "
                        "pool capacity). Lower it for a faster partial snapshot."
                    ),
                    "default": 512,
                },
            },
            "required": [],
        },
    },
    # ---- client ----
    {
        "name": "client_list",
        "description": (
            "List every connected client while the game is HALTED: its uuid, "
            "flags, and local-space center. Drives the C DEBUG_Client_Scanner "
            "(`debug_get_client_scanner(&game)`), walking m_next_client. The "
            "local_space_center field is the diagnostic for a stark center jump "
            "(e.g. {0,63,2} while the manager center is {0,1,3}) that the "
            "incremental local-space scroll path cannot absorb without overflowing "
            "the process pool."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_iter": {
                    "type": "integer",
                    "description": (
                        "Max client slots to walk before stopping (default is the "
                        "client pool max). Lower it for a faster partial list."
                    ),
                },
            },
            "required": [],
        },
    },
    {
        "name": "client_actions",
        "description": (
            "Snapshot the current client's game-action queue while the game is "
            "HALTED: the inbound/outbound queue lengths plus a by-kind tally of the "
            "queue. Drives the C DEBUG_Client_Scanner, walking "
            "m_next_game_action__<direction>. This is the diagnostic for a queue "
            "CLOG — e.g. a world-load that mass-drops global spaces parks thousands "
            "of Global_Space__Store actions in the outbound queue."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["outbound", "inbound"],
                    "description": "Which queue to tally (default 'outbound').",
                    "default": "outbound",
                },
                "max_iter": {
                    "type": "integer",
                    "description": (
                        "Max actions to walk before stopping (default is a "
                        "representative sample of the queue). Raise it for a full "
                        "tally of a very large queue."
                    ),
                },
            },
            "required": [],
        },
    },
    # ---- input ----
    {
        "name": "input_read",
        "description": "Dump the current input state (flags, mouse position, delta).",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "input_write",
        "description": (
            "Drive or drop an input flag. Use 'drive' to set the flag, 'drop' to clear it."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "flag": {
                    "type": "string",
                    "description": (
                        "Input flag name (e.g. FORWARD, LEFT, RIGHT, CLICK). "
                        "See Input_Flags__u32 for the full list."
                    ),
                },
                "action": {
                    "type": "string",
                    "enum": ["drive", "drop"],
                    "description": "Whether to set ('drive') or clear ('drop') the flag.",
                },
            },
            "required": ["flag"],
        },
    },
    # ---- ui ----
    {
        "name": "ui_list",
        "description": (
            "List all UI elements across all UI managers."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "ui_invoke",
        "description": (
            "Invoke a handler on a UI element. All handlers except 'transformed' "
            "are supported."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_ptr": {
                    "type": "string",
                    "description": "Hex pointer to the UI_Element (from ui_list).",
                },
                "handler": {
                    "type": "string",
                    "description": (
                        "Handler name: clicked, dragged, dropped, receive_drop, "
                        "held, typed, compose, dispose."
                    ),
                },
                "dropped_ptr": {
                    "type": "string",
                    "description": "For 'receive_drop': the dropped element pointer.",
                },
                "symbol": {
                    "type": "string",
                    "description": "For 'typed': the character symbol to pass.",
                },
            },
            "required": ["element_ptr", "handler"],
        },
    },
    # ---- graphics ----
    {
        "name": "graphics_screenshot",
        "description": "Capture a screenshot of the current game frame.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "Output file path (defaults to /tmp/lav-screen-<uuid>.png).",
                }
            },
            "required": []
        },
    },
    # ---- audio ----
    {
        "name": "audio_list",
        "description": "List audio devices/sources. Currently unsupported.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "audio_listen",
        "description": "Listen to an audio source. Currently unsupported.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]


# Build a lookup: tool_name -> tool definition
_TOOL_BY_NAME: dict[str, dict[str, Any]] = {t["name"]: t for t in TOOL_DEFINITIONS}


class MCPAdapter:
    """Adapts MCP tool calls to LavSession.invoke().

    This adapter:
    1. Validates that the tool name is in TOOL_DEFINITIONS.
    2. Maps the MCP tool name to a command alias via get_command_alias().
    3. Forwards arguments to LavSession.invoke().
    4. Translates CommandError exceptions into user-friendly error messages.
    """

    def __init__(self, session: LavSession):
        self._session = session
        self._tool_lock = False  # Simple lock flag
        self._log_file: str | None = None
        import time
        self._time = time  # Store time module reference

    def set_log_file(self, log_file: str | None) -> None:
        """Set the log file for MCP tool calls and GDB response logging."""
        self._log_file = log_file
        # Also propagate to GDBSession for GDB response logging
        if log_file and hasattr(self._session, 'gdb'):
            self._session.gdb._log_file = log_file
            self._session.gdb._log_all_responses = True

    @property
    def session(self) -> LavSession:
        """Return the backing LavSession."""
        return self._session

    def list_tools(self) -> list[dict[str, Any]]:
        """Return the list of available MCP tools."""
        return TOOL_DEFINITIONS[:]

    def get_tool(self, name: str) -> dict[str, Any] | None:
        """Return a specific tool definition, or None if not found."""
        return _TOOL_BY_NAME.get(name)

    def dispatch_tool(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> str:
        """Dispatch an MCP tool call to the appropriate scanner driver.

        Args:
            name: The MCP tool name (e.g., "session_start", "step").
            arguments: The tool arguments dict (from MCP protocol).

        Returns:
            The result string from the tool.

        Raises:
            CommandError: If the tool is unknown or invocation fails.
        """
        if name not in _TOOL_BY_NAME:
            raise CommandError(f"Unknown tool: '{name}'")

        # Map MCP tool name to command alias
        alias = get_command_alias(name)
        if alias is None:
            # For tools not in COMMAND_ALIASES, use the tool name itself
            alias = name

        # Merge defaults from schema
        tool_def = _TOOL_BY_NAME[name]
        schema_props = tool_def.get("inputSchema", {}).get("properties", {})
        merged_args: dict[str, Any] = {}

        if arguments:
            merged_args.update(arguments)

        # Apply schema defaults
        for prop_name, prop_def in schema_props.items():
            if prop_name not in merged_args and "default" in prop_def:
                merged_args[prop_name] = prop_def["default"]

        try:
            response = self._session.invoke(alias, **merged_args)
            self._log_tool_call(name, merged_args, response)
            return response
        except CommandError as e:
            self._log_tool_call(name, merged_args, str(e))
            raise
        except Exception as e:
            self._log_tool_call(name, merged_args, f"{type(e).__name__}: {e}")
            raise

    def _log_tool_call(self, tool_name: str, arguments: dict, response: str) -> None:
        """Log a tool call and its response to the log file."""
        import json
        if self._log_file is None:
            return
        try:
            record = {
                "timestamp": self._time.time(),
                "tool": tool_name,
                "arguments": arguments,
                "response_len": len(response),
                "response": response,
            }
            with open(self._log_file, "a") as f:
                f.write(json.dumps(record) + "\n")
                f.flush()
        except OSError:
            pass  # logging is best-effort
