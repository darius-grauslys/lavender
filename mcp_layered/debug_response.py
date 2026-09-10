"""GDB/MI response object model.

Replaces raw dict parsing of pygdbmi output with a rich, typed class hierarchy.

This module does NOT import pygdbmi. It defines the object model for parsing
GDB/MI JSON responses produced by pyygdbmi's GdbController.get_gdb_response().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResponseType(str, Enum):
    """Top-level GDB/MI response categories."""

    TARGET = "target"      # %..., @..., &..., ~... — target output
    RESULT = "result"      # ^done, ^error, ^running, ^connected
    NOTIFY = "notify"      # *stopped, +=breakpoint-modified, etc.
    PROMPT = "prompt"      # (gdb) prompt marker (empty dict from pygdbmi)


class StoppedReason(str, Enum):
    """Values for notify payload 'reason' when type is notify/stopped."""

    BREAKPOINT_HIT = "breakpoint-hit"
    SIGNAL_RECEIVED = "signal-received"
    FUNCTION_DONE = "function-finished"
    SINGLE_STEP = "single-step"
    WATCHPOINT_HIT = "watchpoint-triggered"
    READ_WATCHPOINT_HIT = "read-watchpoint-triggered"
    ACCESS_WATCHPOINT_HIT = "access-watchpoint-triggered"
    EXCEPTION_RECEIVED = "exception-received"
    EXIT = "exited"
    EXIT_NORMALLY = "exited-normally"
    EXIT_SIGNALED = "exited-signalled"
    EXIT_FAILED = "exited-with-signal"


@dataclass
class Frame:
    """A single stack frame from GDB."""

    pc: str = ""
    func: str = ""
    args: list[dict[str, str]] = field(default_factory=list)
    file: str = ""
    line: int = 0
    from_line: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Frame":
        return cls(
            pc=payload.get("pc", ""),
            func=payload.get("func", ""),
            args=payload.get("args", []),
            file=payload.get("file", ""),
            line=int(payload.get("line", 0)) if payload.get("line") else 0,
            from_line=payload.get("from", ""),
        )


@dataclass
class Breakpoint:
    """Breakpoint info from a breakpoint-hit notification."""

    number: str = ""
    type: str = ""
    disp: str = ""
    enabled: str = ""
    addr: str = ""
    func: str = ""
    file: str = ""
    line: int = 0
    pending: str = ""
    hits: int = 0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Breakpoint":
        return cls(
            number=payload.get("number", ""),
            type=payload.get("type", ""),
            disp=payload.get("disp", ""),
            enabled=payload.get("enabled", ""),
            addr=payload.get("addr", ""),
            func=payload.get("func", ""),
            file=payload.get("file", ""),
            line=int(payload.get("line", 0)) if payload.get("line") else 0,
            pending=payload.get("pending", ""),
            hits=int(payload.get("times", 0)) if payload.get("times") else 0,
        )


@dataclass
class DebugResponse:
    """A single GDB/MI response record.

    Created from one dict in the list returned by pygdbmi's
    GdbController.get_gdb_response().
    """

    raw: dict[str, Any]
    type: ResponseType = ResponseType.PROMPT
    reason: str = ""
    payload: dict[str, Any] = field(default_factory=dict)

    # Convenience accessors
    bkpt_num: str = ""
    signal: str = ""
    signal_name: str = ""
    signal_code: str = ""
    frame: Frame | None = None
    threads: list[dict[str, Any]] = field(default_factory=list)
    exited_val: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DebugResponse":
        """Parse a single pygdbmi response dict.

        pygdbmi dict format:
            {"type": "notify"|"result"|"console"|"log",
             "message": "stopped"|"done"|null,
             "payload": {...|None},
             "token": None,
             "stream": "stdout"}
        """
        resp = cls(raw=d, payload=d.get("payload") or {})
        msg = d.get("message") or ""
        rtype = d.get("type", "").lower()

        # Classify
        if rtype == "result":
            resp.type = ResponseType.RESULT
            # message is "done", "error", "running", etc.
        elif rtype == "notify":
            resp.type = ResponseType.NOTIFY
            resp.reason = msg
        elif rtype in ("output", "console", "log", "target"):
            resp.type = ResponseType.TARGET
        elif rtype == "":
            # empty dict {} — pygdbmi sends for prompt marker
            resp.type = ResponseType.PROMPT
            return resp
        else:
            resp.type = ResponseType.PROMPT
            return resp

        # Extract notify-specific fields
        if resp.type == ResponseType.NOTIFY:
            _extract_notify(resp)
        elif resp.type == ResponseType.RESULT:
            _extract_result(resp)

        return resp

    # Convenience predicates
    def is_stopped(self) -> bool:
        """True if this is a stopped notification.

        A stopped notification is a NOTIFY with a reason that indicates the
        target stopped. Known reasons include breakpoint-hit, signal-received,
        function-finished, single-step, watchpoint-*, exited*, exception-*,
        and any reason starting with 'exit' (covers GDB variations).
        """
        if self.type != ResponseType.NOTIFY:
            return False
        if not self.reason:
            return False
        # Known stopped reasons
        known = {
            StoppedReason.BREAKPOINT_HIT.value,
            StoppedReason.SIGNAL_RECEIVED.value,
            StoppedReason.FUNCTION_DONE.value,
            StoppedReason.SINGLE_STEP.value,
            StoppedReason.WATCHPOINT_HIT.value,
            StoppedReason.READ_WATCHPOINT_HIT.value,
            StoppedReason.ACCESS_WATCHPOINT_HIT.value,
            StoppedReason.EXCEPTION_RECEIVED.value,
            StoppedReason.EXIT.value,
            StoppedReason.EXIT_NORMALLY.value,
            StoppedReason.EXIT_SIGNALED.value,
            StoppedReason.EXIT_FAILED.value,
        }
        if self.reason in known:
            return True
        # Also match any reason starting with 'exit' (forward compatibility)
        if self.reason.startswith("exit"):
            return True
        return False

    def is_breakpoint_hit(self) -> bool:
        return self.reason == StoppedReason.BREAKPOINT_HIT.value

    def is_signal(self) -> bool:
        return self.reason == StoppedReason.SIGNAL_RECEIVED.value

    def is_error(self) -> bool:
        """True if this is a result with an error message."""
        return self.type == ResponseType.RESULT and self.raw.get("message") == "error"

    def is_success(self) -> bool:
        """True for ^done, ^running, ^connected, ^exit."""
        return (
            self.type == ResponseType.RESULT
            and self.raw.get("message") in ("done", "running", "connected", "exit")
        )


def _extract_notify(resp: DebugResponse) -> None:
    """Extract fields specific to notify responses."""
    payload = resp.payload
    # In pygdbmi: message="stopped", payload["reason"]="breakpoint-hit" etc.
    # Use payload.reason for the specific reason.
    reason = payload.get("reason", resp.reason)
    resp.reason = reason  # update to specific reason

    if reason == StoppedReason.BREAKPOINT_HIT.value:
        # In a stopped notification, the breakpoint number is in 'bkptno'
        resp.bkpt_num = payload.get("bkptno", "")
        resp.frame = Frame.from_payload(
            payload.get("frame", {})
        )

    elif reason == StoppedReason.SIGNAL_RECEIVED.value:
        resp.signal = payload.get("signal", "")
        resp.signal_name = payload.get("signal-name", "")
        resp.signal_code = payload.get("signal-code", "")
        resp.frame = Frame.from_payload(
            payload.get("frame", {})
        )

    elif reason == StoppedReason.FUNCTION_DONE.value:
        resp.bkpt_num = payload.get("bkptno", "")

    elif reason == StoppedReason.SINGLE_STEP.value:
        resp.frame = Frame.from_payload(
            payload.get("frame", {})
        )

    elif reason in (
        StoppedReason.WATCHPOINT_HIT.value,
        StoppedReason.READ_WATCHPOINT_HIT.value,
        StoppedReason.ACCESS_WATCHPOINT_HIT.value,
    ):
        resp.bkpt_num = payload.get("bkptno", "")

    elif reason in (
        StoppedReason.EXIT.value,
        StoppedReason.EXIT_NORMALLY.value,
        StoppedReason.EXIT_SIGNALED.value,
        StoppedReason.EXIT_FAILED.value,
    ):
        resp.exited_val = True

    # Threads (for *_stopped on multi-threaded targets)
    if "threads" in payload:
        resp.threads = payload["threads"]


def _extract_result(resp: DebugResponse) -> None:
    """Extract fields specific to result responses."""
    if resp.raw.get("message") == "error":
        # pygdbmi error payload: payload={"msg": "error description"}
        resp.reason = resp.payload.get("msg", "Unknown error")
    elif resp.raw.get("message") in ("done", "running", "connected"):
        # These carry their data in payload
        pass


def parse(response_list: list[dict[str, Any]]) -> list[DebugResponse]:
    """Parse a list of raw pygdbmi dicts into DebugResponse objects.

    Non-response entries (empty dicts from prompts, None) are filtered out.
    """
    results: list[DebugResponse] = []
    for d in response_list:
        if not isinstance(d, dict):
            continue
        if not d:
            continue
        results.append(DebugResponse.from_dict(d))
    return results


def parse_stream(response_list: list[dict[str, Any]]) -> list[DebugResponse]:
    """Alias for parse() — parse a stream of responses."""
    return parse(response_list)
