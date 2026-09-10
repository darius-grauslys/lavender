"""
debug_ui_utils.py — Debug helpers that invoke UI element handler fields.

Wraps the ``m_*`` function-pointer fields on ``UI_Element`` (defined.h lines
1582-1622) so a human operator can trigger them from the verify_cli REPL while
paused at ``poll_ui_manager__update``.

PRECONDITION
============
The current gdb frame must be ``poll_ui_manager__update``.  In that frame,
``p_game`` and ``p_graphics_window`` are local variables, so we can resolve them
without frame gymnastics.

If the current frame is not ``poll_ui_manager__update``:
- If frame 1 (caller) is ``poll_ui_manager__update`` (gdb stepped into a
  handler), we issue ``finish`` to return to it automatically.
- Otherwise, the helper sets a temporary breakpoint at
  ``poll_ui_manager__update`` and continues until it fires or a 5-second
  timeout expires.  This allows ``ui utils <handler>`` to be invoked from any
  frame in the game loop.

USAGE (from verify_cli REPL)
============================
    harness> ui utils refresh
        (Re)capture the DebugUIScanner, build the JSON table.

    harness> ui utils list
        Print all UI elements found in the table.

    harness> ui utils clicked <element_ptr>
        Invoke m_ui_clicked_handler on the element at <element_ptr>.

    harness> ui utils dragged <element_ptr>
    harness> ui utils dropped <element_ptr>
    harness> ui utils receive_drop <target_ptr> <dropped_ptr>
    harness> ui utils held <element_ptr>
    harness> ui utils typed <element_ptr> <symbol>
    harness> ui utils compose <element_ptr>
    harness> ui utils dispose <element_ptr>

    harness> ui utils transformed <element_ptr>
        (Not yet implemented — writes a stub message.)

The handlers are the raw function pointers stored in the UI_Element struct.
We cast-and-call them (same technique as DebugScannerBase._advance).

See:
    - core/include/defines.h lines 1582-1622 (handler typedefs)
    - core/include/defines.h lines 1671-1696 (UI_Element handler fields)
    - core/source/ui/ui_manager.c:551-554 (poll_ui_manager__update signature)
"""

from __future__ import annotations

import json
import re
from typing import Any

from .debug_scanner_ui import DebugUIScanner
from .gdb_nav_utils import step_frame as _step_frame


# The gdb frame name that is our precondition.
_REQUIRED_FRAME_NAME = "poll_ui_manager__update"

# Handler field names on UI_Element (defines.h lines 1671-1696).
# Map: CLI keyword -> (C struct field name, C function-pointer type name).
_HANDLERS: dict[str, tuple[str, str]] = {
    "clicked": ("m_ui_clicked_handler", "m_UI_Clicked"),
    "dragged": ("m_ui_dragged_handler", "m_UI_Dragged"),
    "dropped": ("m_ui_dropped_handler", "m_UI_Dropped"),
    "receive_drop": ("m_ui_receive_drop_handler", "m_UI_Receive_Drop"),
    "held": ("m_ui_held_handler", "m_UI_Held"),
    "typed": ("m_ui_typed_handler", "m_UI_Typed"),
    "compose": ("m_ui_compose_handler", "m_UI_Compose"),
    "dispose": ("m_ui_dispose_handler", "m_UI_Dispose"),
}


class DebugUIUtils:
    """Drive UI element handler fields against a live gdb target.

    Construct with a GdbController (``gdbmi``) and call :meth:`refresh`
    to (re)capture the scanner table.  Then use the handler methods.

    Every handler method automatically navigates to the ``poll_ui_manager__update``
    frame before proceeding, either by returning from a stepped-into callee
    (``finish``) or by continuing to a breakpoint (5-second timeout).
    """

    def __init__(self, gdbmi) -> None:
        self._gdbmi = gdbmi
        self._scanner: DebugUIScanner | None = None

    # -- frame navigation ------------------------------------------------------ #

    def _navigate_to_frame(self, timeout: float = 5.0) -> None:
        """Ensure gdb is stopped at ``poll_ui_manager__update``, navigating if
        needed.

        Fast path: If the current frame (or its caller at level 1) is already
        ``poll_ui_manager__update``, we're done immediately.  If frame 1 is
        the required frame, ``finish`` returns us there.

        Slow path: If neither frame matches, set a temporary breakpoint at
        ``poll_ui_manager__update`` and continue until it fires (or the
        timeout expires).  This allows handler methods to be invoked from any
        frame in the game loop.

        Args:
            timeout: Maximum seconds to wait for the breakpoint (default 5.0).

        Raises:
            RuntimeError: If navigation fails within the timeout.
        """
        # Fast path: check if we're already in the right frame.
        resp = self._gdbmi.write("-stack-info-frame")
        name = ""
        for rec in resp:
            if isinstance(rec, dict) and rec.get("type") == "result":
                payload = rec.get("payload") or {}
                frame = payload.get("frame") or {}
                name = frame.get("name") or frame.get("func") or ""
                break

        if name == _REQUIRED_FRAME_NAME:
            return

        # Check if frame 1 (caller) is poll_ui_manager__update.
        # This happens when a handler was invoked and stepped into a callee.
        frame1_name = self._get_frame_name(1)
        if frame1_name == _REQUIRED_FRAME_NAME:
            print(f"  [ui utils] returning to {_REQUIRED_FRAME_NAME!r} "
                  f"(was in {name!r})")
            self._gdbmi.write("-exec-finish")
            return

        # Slow path: navigate using step_frame.
        print(f"  [ui utils] navigating to {_REQUIRED_FRAME_NAME!r} ...")
        ok = _step_frame(self._gdbmi, _REQUIRED_FRAME_NAME, timeout=timeout)
        if not ok:
            raise RuntimeError(
                f"Failed to navigate to {_REQUIRED_FRAME_NAME!r} within "
                f"{timeout}s. The game may have exited or hit too many "
                f"unexpected breakpoints."
            )
        print(f"  [ui utils] reached {_REQUIRED_FRAME_NAME!r}")

    def _get_frame_name(self, level: int) -> str:
        """Return the function name at the given stack frame level."""
        resp = self._gdbmi.write(f"-stack-info-frame")
        # -stack-info-frame returns the current frame; we need to select
        # the requested level first, then check, then restore.
        current_level = self._get_current_frame_level()
        self._gdbmi.write(f"-stack-select-frame {level}")
        resp = self._gdbmi.write("-stack-info-frame")
        name = ""
        for rec in resp:
            if isinstance(rec, dict) and rec.get("type") == "result":
                payload = rec.get("payload") or {}
                frame = payload.get("frame") or {}
                name = frame.get("name") or frame.get("func") or ""
                break
        # Restore original frame.
        self._gdbmi.write(f"-stack-select-frame {current_level}")
        return name

    def _get_current_frame_level(self) -> int:
        """Return the current gdb frame level (0 = innermost)."""
        resp = self._gdbmi.write("-stack-info-frame")
        for rec in resp:
            if isinstance(rec, dict) and rec.get("type") == "result":
                payload = rec.get("payload") or {}
                frame = payload.get("frame") or {}
                level_str = frame.get("level", "0")
                return int(level_str)
        return 0

    # -- scanner table --------------------------------------------------------- #

    def refresh(self) -> None:
        """Re-capture the DebugUIScanner and rebuild the JSON table."""
        self._scanner = DebugUIScanner(self._gdbmi)
        repr_str = self._scanner.get_scanner()
        if repr_str is None:
            raise RuntimeError(
                "get_scanner() returned None — check the debug symbols."
            )
        # Force table build (also caches it).
        self._scanner.get_table()
        print(f"  scanner captured: {repr_str[:200]}")

    def _ensure_scanner(self) -> DebugUIScanner:
        """Return the cached scanner, refreshing if necessary."""
        if self._scanner is None:
            self.refresh()
        return self._scanner

    def get_table(self) -> dict:
        """Return the scanner's JSON table (the single source of truth)."""
        return self._ensure_scanner().get_table()

    def list_elements(self) -> list[dict]:
        """Return a flat list of all UI elements from the table.

        Each entry: ``{"manager_ptr": str, "element_ptr": str,
                        "uuid": str, "kind": str}``
        """
        table = self.get_table()
        elements: list[dict] = []
        for mgr_ptr, mgr in table.get("ui_managers", {}).items():
            for el_ptr, el in mgr.get("ui_elements", {}).items():
                entries = {
                    "manager_ptr": mgr_ptr,
                    "element_ptr": el_ptr,
                    "uuid": el.get("uuid", ""),
                    "kind": el.get("kind", ""),
                }
                # Add the raw element pointer for lookup
                entries["element_ptr_raw"] = el_ptr
                elements.append(entries)
        return elements

    # -- pointer resolution ---------------------------------------------------- #

    @staticmethod
    def _resolve_element_ptr(table: dict, element_ptr: str) -> str | None:
        """Find the given element pointer in the table, return it if found.

        ``element_ptr`` may be a bare hex (``"0x2000"``) or include a
        symbol (``"0x5555555704f0 <adv_element>"``); we match on the hex
        prefix.
        """
        hex_prefix = element_ptr.split()[0]  # strip "<symbol>"
        for mgr_ptr, mgr in table.get("ui_managers", {}).items():
            for el_ptr in mgr.get("ui_elements", {}):
                if el_ptr.split()[0] == hex_prefix:
                    return el_ptr
        return None

    # -- handler invocation ---------------------------------------------------- #

    def _invoke_handler(
        self,
        element_ptr: str,
        field_name: str,
        func_type: str,
        extra_args: str = "",
    ) -> None:
        """Invoke a handler field on a UI_Element via cast-and-call.

        Issues::

            call ((FuncType)((UI_Element *)element_ptr)->field_name)(
                (UI_Element *)element_ptr, p_game, p_graphics_window
            )

        from the current (poll_ui_manager__update) frame.

        *element_ptr* is a ``UI_Element *`` (single indirection) from the
        scanner table.  We cast it to ``(UI_Element *)`` before using ``->``
        to access handler fields.

        After the call, gdb may have stepped into the handler.  We issue
        ``finish`` to return to ``poll_ui_manager__update`` if the frame
        changed.
        """
        # Precondition: must be in poll_ui_manager__update.
        self._navigate_to_frame()

        # element_ptr is a UI_Element * from the scanner table.
        # Cast it to (UI_Element *) before using -> to access handler fields.
        # Pattern: ((FuncType)((UI_Element *)ptr)->field)((UI_Element *)ptr, p_game, p_gfx_window)
        call_expr = (
            f"call (({func_type})((UI_Element *){element_ptr})->{field_name})("
            f"(UI_Element *){element_ptr}, p_game, p_graphics_window"
        )
        if extra_args:
            call_expr += f", {extra_args}"
        call_expr += ")"

        resp = self._gdbmi.write(
            f'-interpreter-exec console "{call_expr}"'
        )
        self._print_response(resp)
        self._return_to_frame()

    def _print_response(self, resp) -> None:
        """Print console output from a gdb response."""
        for rec in resp:
            if isinstance(rec, dict):
                rtype = rec.get("type", "?")
                payload = rec.get("payload")
                if rtype == "console" and payload:
                    print(f"  [console] {payload}")

    # -- public handler methods ------------------------------------------------ #

    def clicked(self, element_ptr: str) -> None:
        """Invoke ``m_ui_clicked_handler`` on the given element."""
        self._invoke_for_handler("clicked", element_ptr)

    def dragged(self, element_ptr: str) -> None:
        """Invoke ``m_ui_dragged_handler`` on the given element."""
        self._invoke_for_handler("dragged", element_ptr)

    def dropped(self, element_ptr: str) -> None:
        """Invoke ``m_ui_dropped_handler`` on the given element."""
        self._invoke_for_handler("dropped", element_ptr)

    def receive_drop(self, target_ptr: str, dropped_ptr: str) -> None:
        """Invoke ``m_ui_receive_drop_handler`` on *target_ptr* with *dropped_ptr*."""
        self._invoke_for_receive_drop(target_ptr, dropped_ptr)

    def held(self, element_ptr: str) -> None:
        """Invoke ``m_ui_held_handler`` on the given element."""
        self._invoke_for_handler("held", element_ptr)

    def typed(self, element_ptr: str, symbol: str) -> None:
        """Invoke ``m_ui_typed_handler`` on the given element with *symbol*."""
        self._invoke_for_typed(element_ptr, symbol)

    def compose(self, element_ptr: str) -> None:
        """Invoke ``m_ui_compose_handler`` on the given element."""
        self._invoke_for_handler("compose", element_ptr)

    def dispose(self, element_ptr: str) -> None:
        """Invoke ``m_ui_dispose_handler`` on the given element.

        WARNING: This calls the dispose handler which may free the element.
        The scanner table will be stale after this call — refresh before
        using the scanner again.
        """
        self._invoke_for_handler("dispose", element_ptr)
        # Invalidate the cached scanner since element memory may have changed.
        self._scanner = None

    def transformed(self, element_ptr: str) -> None:
        """Invoke ``m_ui_transformed_handler`` on the given element.

        NOT YET IMPLEMENTED — the transformed handler requires a hitbox AABB
        and a position vector, which are non-trivial to resolve from the
        current frame.  This is a stub that writes to stdout.
        """
        print(
            "[stub] m_ui_transformed_handler is not yet implemented. "
            "The handler requires a Hitbox_AABB and Vector__3i32 position "
            "which need non-trivial resolution from the current frame."
        )

    # -- internal helper ------------------------------------------------------- #

    def _invoke_for_handler(self, handler_key: str, element_ptr: str) -> None:
        """Resolve *element_ptr* in the table, then invoke the handler."""
        self._navigate_to_frame()
        table = self.get_table()

        resolved = self._resolve_element_ptr(table, element_ptr)
        if resolved is None:
            raise ValueError(
                f"Could not find element {element_ptr!r} in the scanner table. "
                f"Run 'ui utils list' to see available elements."
            )

        field_name, func_type = _HANDLERS[handler_key]
        self._invoke_handler(resolved, field_name, func_type)

    def _invoke_for_receive_drop(
        self, target_ptr: str, dropped_ptr: str
    ) -> None:
        """Resolve both pointers and invoke receive_drop handler."""
        self._navigate_to_frame()
        table = self.get_table()

        resolved_target = self._resolve_element_ptr(table, target_ptr)
        if resolved_target is None:
            raise ValueError(
                f"Could not find element {target_ptr!r} in the scanner table."
            )

        resolved_dropped = self._resolve_element_ptr(table, dropped_ptr)
        if resolved_dropped is None:
            raise ValueError(
                f"Could not find element {dropped_ptr!r} in the scanner table."
            )

        field_name, func_type = _HANDLERS["receive_drop"]
        call_expr = (
            f"call (({func_type})((UI_Element *){resolved_target})->{field_name})("
            f"(UI_Element *){resolved_target}, "
            f"(UI_Element *){resolved_dropped}, p_game, p_graphics_window)"
        )
        resp = self._gdbmi.write(
            f'-interpreter-exec console "{call_expr}"'
        )
        self._print_response(resp)
        self._return_to_frame()

    def _invoke_for_typed(self, element_ptr: str, symbol: str) -> None:
        """Resolve element pointer and invoke typed handler with a char."""
        self._navigate_to_frame()
        table = self.get_table()

        resolved = self._resolve_element_ptr(table, element_ptr)
        if resolved is None:
            raise ValueError(
                f"Could not find element {element_ptr!r} in the scanner table."
            )

        field_name, func_type = _HANDLERS["typed"]
        call_expr = (
            f"call (({func_type})((UI_Element *){resolved})->{field_name})("
            f"(UI_Element *){resolved}, p_game, p_graphics_window, '{symbol}')"
        )
        resp = self._gdbmi.write(
            f'-interpreter-exec console "{call_expr}"'
        )
        self._print_response(resp)
        self._return_to_frame()

    # -- internal helper ------------------------------------------------------- #

    def _return_to_frame(self) -> None:
        """Return to poll_ui_manager__update if gdb stepped into a handler.

        After a ``call`` that invokes a function pointer, gdb may have
        stepped into the callee.  We issue ``finish`` (which runs until the
        current function returns) to get back to ``poll_ui_manager__update``.
        If we're already there, this is effectively a no-op.
        """
        resp = self._gdbmi.write("-stack-info-frame")
        current_name = ""
        for rec in resp:
            if isinstance(rec, dict) and rec.get("type") == "result":
                payload = rec.get("payload") or {}
                frame = payload.get("frame") or {}
                current_name = frame.get("name") or frame.get("func") or ""
                break

        if current_name != _REQUIRED_FRAME_NAME:
            print(f"  [ui utils] returning to {_REQUIRED_FRAME_NAME!r} "
                  f"(was in {current_name!r})")
            self._gdbmi.write("-exec-finish")
            # Select main frame to ensure we're back where we started.
            self._gdbmi.write("-stack-select-frame 0")

    # -- CLI dispatch ---------------------------------------------------------- #

    def do_command(self, args: list[str]) -> bool:
        """Dispatch a CLI subcommand.  Returns True if handled.

        Subcommands:
            refresh                     Re-capture the scanner table.
            list                        List all UI elements.
            <handler> <element_ptr>     Invoke a handler on an element.
            transformed <element_ptr>     Stub invocation (not implemented).
            receive_drop <target> <dropped>
                                        Invoke receive_drop handler.
            typed <element_ptr> <symbol>  Invoke typed handler with a char.
        """
        if not args:
            self._print_usage()
            return True

        cmd = args[0].lower()
        rest = args[1:]

        if cmd == "refresh":
            self.refresh()
            return True

        if cmd == "list":
            elements = self.list_elements()
            if not elements:
                print("  (no elements found)")
            else:
                for el in elements:
                    print(f"  {el['element_ptr']}: "
                          f"kind={el['kind']}, uuid={el['uuid']}")
            return True

        if cmd == "transformed":
            if not rest:
                print("  usage: ui utils transformed <element_ptr>")
                return True
            self.transformed(rest[0])
            return True

        if cmd == "receive_drop":
            if len(rest) < 2:
                print("  usage: ui utils receive_drop <target_ptr> <dropped_ptr>")
                return True
            self.receive_drop(rest[0], rest[1])
            return True

        if cmd == "typed":
            if len(rest) < 2:
                print("  usage: ui utils typed <element_ptr> <symbol>")
                return True
            self.typed(rest[0], rest[1])
            return True

        if cmd in _HANDLERS:
            if not rest:
                print(f"  usage: ui utils {cmd} <element_ptr>")
                return True
            method = getattr(self, cmd)
            method(rest[0])
            return True

        return False

    @staticmethod
    def _print_usage() -> None:
        handlers_str = ", ".join(_HANDLERS.keys())
        print(
            "UI Utils commands:\n"
            "  refresh                           Re-capture the scanner table.\n"
            "  list                              List all UI elements.\n"
            f"  {handlers_str} <element_ptr>     Invoke handler on element.\n"
            "  receive_drop <target> <dropped>   Invoke receive_drop handler.\n"
            "  typed <element_ptr> <symbol>      Invoke typed handler with char.\n"
            "  transformed <element_ptr>         Stub (not implemented).\n"
        )
