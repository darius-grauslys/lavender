"""Layer 3: Scanner drivers and Lavender commands.

This layer holds all the various Lavender Scanner drivers (DebugUIScanner,
ProcessScanner, etc.) as well as individual commands intended to be invoked
(step, start, ui_list, process_watch, etc.).

It exposes API to higher layers: a required `alias` argument to route to a
scanner driver, then **kwargs to provide arguments to the scanner driver.

The scanner driver can reject invocation on grounds of invalid kwargs, which
is raised as an exception.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Callable

# We import the existing scanner drivers and command implementations from
# the mcp/ package to avoid duplicating their logic.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from mcp_layered.layer_lav_config import LavConfig
from mcp_layered.layer_pygdbmi import GDBSession


class CommandError(Exception):
    """Raised when a command cannot be invoked (invalid args, etc.)."""
    pass


# Type alias for scanner driver invoke functions
ScannerDriver = Callable[[GDBSession, LavConfig, dict[str, Any]], str]


# -- Scanner Driver Registry -- #

# Registry: alias -> driver callable
# In the full implementation, this would hold DebugUIScanner, ProcessScanner, etc.
# For now, we create a simplified registry structure.
_DRIVERS: dict[str, ScannerDriver] = {}


def register_driver(alias: str, driver: ScannerDriver) -> None:
    """Register a scanner driver under the given alias."""
    _DRIVERS[alias] = driver


def unregister_driver(alias: str) -> None:
    """Unregister a scanner driver."""
    _DRIVERS.pop(alias, None)


def get_driver(alias: str) -> ScannerDriver | None:
    """Get a registered scanner driver by alias."""
    return _DRIVERS.get(alias)


def list_drivers() -> list[str]:
    """List all registered driver aliases."""
    return list(_DRIVERS.keys())


def invoke(alias: str, gdb: GDBSession, config: LavConfig, **kwargs: Any) -> str:
    """Route a command invocation to the appropriate scanner driver.

    Args:
        alias: The scanner driver alias (e.g., "ui", "process", "step").
        gdb: The GDBSession to use for GDB interaction.
        config: The LavConfig for this session.
        **kwargs: Arguments to pass to the scanner driver.

    Returns:
        The result string from the scanner driver.

    Raises:
        CommandError: If the alias is not registered or kwargs are invalid.
    """
    driver = get_driver(alias)
    if driver is None:
        raise CommandError(f"Unknown scanner driver alias: '{alias}'. "
                          f"Registered: {list_drivers()}")

    try:
        return driver(gdb, config, kwargs)
    except CommandError:
        raise
    except Exception as e:
        raise CommandError(f"Driver '{alias}' failed: {type(e).__name__}: {e}")


# -- Built-in commands (wrappers around scanner drivers) -- #

# These command aliases map to specific scanner driver functionality.
# In the full implementation, each would be a method on a scanner class.

# Command alias constants for the MCP tool interface
# Maps MCP tool name -> command alias (drives scanner driver invocation)
COMMAND_ALIASES = {
    # Session commands
    "session_start": "session_start",
    "session_status": "session_status",
    "session_stop": "session_stop",
    # Navigation commands
    "navigate_step": "step",  # MCP tool name -> driver alias
    "step": "step",            # CLI shorthand
    "navigate_source": "navigate_source",
    "bt": "navigate_source",  # CLI shorthand
    # Core dump commands
    # Core dump commands
    "core_dump": "core_dump",
    "core_load": "core_load",
    "core_reset": "core_reset",
    # Process commands
    "process_list": "process_list",
    "process_watch": "process_watch",
    # Input commands
    "input_read": "input_read",
    "input_write": "input_write",
    # UI commands
    "ui_list": "ui_list",
    "ui_invoke": "ui_invoke",
    # Graphics commands
    "graphics_screenshot": "graphics_screenshot",
    # Audio commands
    "audio_list": "audio_list",
    "audio_listen": "audio_listen",
}


def get_command_alias(mcp_tool_name: str) -> str | None:
    """Map an MCP tool name to a command alias.

    Returns None if the tool name is not recognized.
    """
    return COMMAND_ALIASES.get(mcp_tool_name)


def get_required_kwargs(alias: str) -> list[str]:
    """Return the list of required kwargs for a given command alias.

    This is used for input validation before invoking a driver.
    """
    # In the full implementation, this would be metadata from the driver.
    # For now, return empty list (no required kwargs).
    return []
