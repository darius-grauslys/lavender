"""
gdb_frame_controller.py — Low-level gdb plumbing shared by all debug drivers.

Provides GDBFrameController, which wraps a pygdbmi GdbController and offers:

  * a small stack of saved gdb frame levels, plus push/pop helpers,
  * low-level wrappers over pygdbmi:
      - _call(expr)  — the CLI ``call`` (return values only in console stream)
      - _exec(stmt)  — arbitrary console statement (e.g. ``set $x = ...``)
      - _eval(expr)  — ``-data-evaluate-expression`` (the clean way to read
                        a value because pygdbmi puts it in the result payload
                        rather than a console stream record)

All frame-dependent helpers in the debug drivers subclass this and wrap their
work in push_main_frame() / pop_frame() so the caller's frame context is always
restored, even on error.
"""

from __future__ import annotations

from pygdbmi.gdbcontroller import GdbController

_HAS_PYGDBMI = True


class GDBFrameController:
    """Shared gdb plumbing: frame stack + low-level MI primitives."""

    def __init__(self, gdbmi: GdbController) -> None:
        self._gdbmi = gdbmi
        self._frame_stack: list[int] = []

    # -- frame management --------------------------------------------------- #

    def _current_frame_level(self) -> int:
        resp = self._gdbmi.write("-stack-info-frame")
        for rec in resp:
            if rec.get("type") == "result" and rec.get("message") == "done":
                payload = rec.get("payload") or {}
                frame = payload.get("frame") or {}
                return int(frame.get("level", 0))
        return 0

    def push_frame(self, n: int) -> None:
        """Save the current frame and select frame *n*."""
        self._frame_stack.append(self._current_frame_level())
        self._gdbmi.write(f"-stack-select-frame {n}")

    def push_main_frame(self) -> None:
        """Select the innermost (main) frame after saving the current one."""
        self.push_frame(0)

    def pop_frame(self) -> None:
        """Restore the most recently saved frame."""
        if not self._frame_stack:
            return
        level = self._frame_stack.pop()
        self._gdbmi.write(f"-stack-select-frame {level}")

    # -- low level gdb primitives ------------------------------------------ #

    def _call(self, expr: str) -> list:
        """Invoke *expr* as a gdb ``call`` expression; return the response.

        Note: a ``call``'s return value is *not* placed in the parsed MI
        result payload (it shows up only as console output), so callers that
        need the value should use ``_eval`` instead.
        """
        return self._gdbmi.write(f'-interpreter-exec console "call {expr}"')

    def _batch_call(self, exprs: list[str]) -> list[str]:
        """Invoke multiple function-pointer calls in a single gdb ``call``.

        Composes a C brace expression like::

            call {func1(), func2(), func3()}

        This lets us advance the scanner multiple steps with a single gdb
        round-trip, dramatically reducing overhead (each round-trip to gdb
        has a high fixed cost, similar to ADB on Android).

        Returns the console stream records from the response, which contain
        the struct array printed by gdb.  Callers parse the array to extract
        scanner positions (pointers, UUIDs, kinds).
        """
        # Build the brace expression: {expr1(), expr2(), ...}
        batch = "{" + ", ".join(exprs) + "}"
        resp = self._gdbmi.write(f'-interpreter-exec console "call {batch}"')
        # Filter for console stream records (the struct array is printed here).
        return [rec for rec in resp if rec.get("type") == "console"]

    def _exec(self, stmt: str) -> list:
        """Run an arbitrary gdb console statement (e.g. ``set $x = ...``)."""
        return self._gdbmi.write(f'-interpreter-exec console "{stmt}"')

    def _eval(self, expr: str) -> str | None:
        """Evaluate *expr* via ``-data-evaluate-expression``.

        Returns the printed value (in ``payload['value']``) or ``None``.
        This is the reliable way to read a value back from gdb as JSON.
        """
        resp = self._gdbmi.write(f"-data-evaluate-expression {expr}")
        for rec in resp:
            if rec.get("type") == "result" and rec.get("message") == "done":
                return (rec.get("payload") or {}).get("value")
        return None
