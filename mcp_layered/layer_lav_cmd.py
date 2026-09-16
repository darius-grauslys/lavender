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
import re
import sys
from fnmatch import fnmatch
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

    # Resolve any `[]` selectors in string kwargs against the session's cached
    # scanner table (see resolve_value) before dispatching. Non-string kwargs
    # pass through untouched. This is the single seam: a future path-query DSL
    # extends resolve_value, never the dispatch call sites.
    kwargs = {k: resolve_value(gdb, v) for k, v in kwargs.items()}

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
    # Trace toggle
    "trace": "trace",
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
    "process_handler": "process_handler",
    "process_pool": "process_pool",
    # Client commands
    "client_list": "client_list",
    "client_actions": "client_actions",
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


# -- `[]` selector resolution (pointer delimiters) --------------------------- #
#
# A command argument may embed a `[...]` selector to name a scanner-table entry
# by a stable property instead of a raw pointer, e.g.:
#     ui invoke clicked [type=*Button,n=2]
# The selector is resolved against the session's cached scanner table
# (GDBSession._ui_cache, populated by ui_list and cleared by the
# initialize_ui_manager hook) and substituted for the raw pointer before the
# driver runs.
#
# The UI's element pointers are stable pool-slot addresses (they do not dangle
# across a UI rebuild), so a cached entry stays address-valid; only its
# contents (kind/handlers) can change, which `ui list` + the init hook refresh.
#
# FORWARD-COMPATIBLE SEAM: `invoke()` only ever calls resolve_value(). A future
# full path-query DSL ("a.b.c.[idx=2].e.f.[type=*X]") extends
# parse_selector()/select_from()/resolve_value() to walk dotted paths; the
# dispatch call sites do not change.

# A `[...]` selector: the body contains no nested brackets (space-free tokens).
_SELECTOR_RE = re.compile(r"\[([^\[\]]*)\]")


def parse_selector(body: str) -> dict:
    """Parse a selector body into a dict.

    Supported now:
      - 'type'  wildcard (fnmatch) matched against an item's 'kind'
      - 'n'     1-based ordinal within the type-matched set (n=1 is "first")
      - 'idx'   0-based positional index into the (filtered) set
    Unknown keys are preserved verbatim so a future DSL extends parsing without
    breaking existing selectors.
    """
    sel: dict = {}
    for part in body.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            k, v = k.strip(), v.strip()
        else:
            k, v = part, ""
        if k in ("n", "idx"):
            sel[k] = int(v) if v.isdigit() else None
        else:
            sel[k] = v
    return sel


def _flatten_ui_elements(cache) -> list:
    """Flatten a ui_list table into an ordered list of element items.

    Order matches ui_list's display order (managers sorted by ptr, then
    elements sorted by ptr), so "first/second" are deterministic across
    re-lists of an unchanged UI. Each item: {'ptr','kind','uuid','manager'}.
    """
    items: list = []
    if not cache:
        return items
    for mgr_ptr, mgr in sorted((cache.get("ui_managers") or {}).items()):
        for el_ptr, info in sorted(((mgr or {}).get("ui_elements") or {}).items()):
            items.append({
                "ptr": el_ptr,
                "kind": (info or {}).get("kind", ""),
                "uuid": (info or {}).get("uuid"),
                "manager": mgr_ptr,
            })
    return items


def select_from(items: list, sel: dict):
    """Apply a selector to a flat item list; return the matching item or None.

    'type' filters by fnmatch on the item's 'kind'; 'n' picks the 1-based
    ordinal within the filtered set; 'idx' picks the 0-based position. With no
    n/idx, a single candidate is returned, else None (ambiguous/no match).
    """
    cands = list(items)
    if sel.get("type"):
        cands = [it for it in cands
                 if fnmatch(str(it.get("kind", "")), sel["type"])]
    if sel.get("n") is not None:
        i = sel["n"] - 1
        return cands[i] if 0 <= i < len(cands) else None
    if sel.get("idx") is not None:
        return cands[sel["idx"]] if 0 <= sel["idx"] < len(cands) else None
    return cands[0] if len(cands) == 1 else None


def resolve_value(gdb, value):
    """Resolve any `[...]` selector(s) in a string value against the
    per-session UI cache, substituting each matched element's pointer.

    This is the single seam the dispatcher uses for all `[]` resolution; a
    future path-query DSL extends it here (parse dotted paths, walk the table)
    rather than touching call sites. Non-string values and strings with no
    `[...]` are returned unchanged.
    """
    if not isinstance(value, str) or not _SELECTOR_RE.search(value):
        return value
    items = _flatten_ui_elements(getattr(gdb, "_ui_cache", None))

    def _sub(match):
        sel = parse_selector(match.group(1))
        item = select_from(items, sel)
        if item is None:
            raise CommandError(
                f"selector '{match.group(0)}' matched no UI element "
                f"(run `ui list` to refresh the cache first)")
        return str(item.get("ptr"))

    return _SELECTOR_RE.sub(_sub, value)
