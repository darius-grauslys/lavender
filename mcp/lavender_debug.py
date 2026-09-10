"""
lavender_debug.py — Shared utilities and debug-domain constants for the harness.

Contains:
  * Input_Flags__u32 — mirrors the INPUT_* macros in platform_defaults.h.
  * parse_hex / _extract_call_value / _vector__3i32_literal — helpers for
    rendering C expressions and extracting values from gdb response streams.

The bit-flag definitions intentionally duplicate (a DRY-violating mirror of)
the INPUT_* macros in core/include/platform_defaults.h so the harness can build
flag bitmasks without parsing C headers.
"""

from __future__ import annotations

import re
from enum import IntEnum


# --------------------------------------------------------------------------- #
#  Input flags  (mirror of INPUT_* in platform_defaults.h)
# --------------------------------------------------------------------------- #
class Input_Flags__u32(IntEnum):
    """Mirror of the INPUT_* bit-flags in platform_defaults.h.

    #define INPUT_FORWARD   (1<<0)
    #define INPUT_LEFT      (INPUT_FORWARD<<1)
    ...
    #define INPUT_CLICK     (INPUT_TURN_LEFT<<1)
    """

    NONE = 0
    FORWARD = 1 << 0
    LEFT = 1 << 1
    RIGHT = 1 << 2
    BACKWARD = 1 << 3
    GAME_SETTINGS = 1 << 4
    LOCKON = 1 << 5
    USE = 1 << 6
    USE_SECONDARY = 1 << 7
    EXAMINE = 1 << 8
    CONSUME = 1 << 9
    TURN_RIGHT = 1 << 10
    TURN_LEFT = 1 << 11
    CLICK = 1 << 12


# --------------------------------------------------------------------------- #
#  C expression rendering
# --------------------------------------------------------------------------- #
def _vector__3i32_literal(x: int, y: int, z: int) -> str:
    """Render a (Vector__3i32){x, y, z} compound-literal for gdb.

    A bare brace initializer is not valid as a C function argument, so the
    cast prefix is required.
    """
    return f"(Vector__3i32){{{x}, {y}, {z}}}"


# --------------------------------------------------------------------------- #
#  Response parsing
# --------------------------------------------------------------------------- #
_CALL_VALUE_RE = re.compile(
    r"=\s*(?:\([^)]*\)\s*)?(0x[0-9a-fA-F]+|true|false)"
)

_HEX_RE = re.compile(r"0x[0-9a-fA-F]+")


def _extract_call_value(resp: list) -> str | None:
    """Pull a return value out of a ``call`` console-stream response.

    pygdbmi's ``-interpreter-exec console "call ..."`` only reports a
    function's return value as console output (e.g.
    ``$1 = (Process *) 0x55558018 <f>`` or ``$2 = true``); the parsed MI
    results record's payload is ``None``. This scans the console stream
    records and returns the address, boolean, or ``None`` if nothing was found.
    """
    for rec in resp:
        payload = rec.get("payload")
        if rec.get("type") == "console" and payload:
            m = _CALL_VALUE_RE.search(payload)
            if m:
                return m.group(1)
    return None


def parse_hex(value: str | None) -> str | None:
    """Extract the leading hex address from a gdb value string.

    e.g. "0x5555555551c3 <adv_element>" -> "0x5555555551c3"
         "0x11223344"                     -> "0x11223344"
    """
    if not value:
        return None
    m = _HEX_RE.search(value)
    return m.group(0) if m else None
