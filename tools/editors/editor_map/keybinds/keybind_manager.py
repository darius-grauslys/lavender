"""
Keybind manager with override stack.

See spec section 4.4:
- set_base_keybinds(dict)
- push_override(dict)
- pop_override()
- clear_override_stack()
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from keybinds.keybind import KeyCombo, KeybindCallback

if TYPE_CHECKING:
    from ui.message_hud import MessageHUD


class KeybindManager:
    """
    Manages keybinds with a stack-based override system.

    Base keybinds are used when the override stack is empty.
    Each push_override adds callbacks on top; pop_override
    removes the most recent push.

    If a ``MessageHUD`` is attached via ``set_message_hud``,
    push/pop operations are logged as INFO messages.
    """

    def __init__(self):
        self._base: Dict[KeyCombo, KeybindCallback] = {}
        # Per-key stack of override callbacks
        self._override_stacks: Dict[KeyCombo, List[KeybindCallback]] = \
            defaultdict(list)
        # Stack of key-sets pushed by each push_override call
        self._callee_override_stack: List[Set[KeyCombo]] = []
        self._message_hud: Optional[MessageHUD] = None

    def set_message_hud(self, hud: MessageHUD) -> None:
        """Attach a MessageHUD for logging keybind push/pop events."""
        self._message_hud = hud

    def set_base_keybinds(
            self, binds: Dict[KeyCombo, KeybindCallback]) -> None:
        """Set the base (lowest priority) keybinds."""
        self._base = dict(binds)

    def push_override(
            self, binds: Dict[KeyCombo, KeybindCallback]) -> None:
        """Push a set of keybind overrides onto the stack."""
        keys: Set[KeyCombo] = set()
        for combo, callback in binds.items():
            self._override_stacks[combo].append(callback)
            keys.add(combo)
        self._callee_override_stack.append(keys)
        if self._message_hud and binds:
            count = len(binds)
            self._message_hud.info(
                f"Keybinds pushed: {count} override(s) "
                f"(stack depth: {len(self._callee_override_stack)})")

    def pop_override(self) -> None:
        """Pop the most recent set of keybind overrides."""
        if not self._callee_override_stack:
            return
        keys = self._callee_override_stack.pop()
        for combo in keys:
            stack = self._override_stacks.get(combo)
            if stack:
                stack.pop()
                if not stack:
                    del self._override_stacks[combo]
        if self._message_hud:
            self._message_hud.info(
                f"Keybinds popped: {len(keys)} override(s) "
                f"(stack depth: {len(self._callee_override_stack)})")

    def clear_override_stack(self) -> None:
        """Remove all overrides, returning to base keybinds."""
        self._override_stacks.clear()
        self._callee_override_stack.clear()

    def get_callback(self, combo: KeyCombo) -> KeybindCallback | None:
        """Get the active callback for a key combo, or None."""
        stack = self._override_stacks.get(combo)
        if stack:
            return stack[-1]
        return self._base.get(combo)

    def fire(self, combo: KeyCombo) -> bool:
        """
        Fire the keybind for the given combo.
        Returns True if a callback was found and invoked.
        """
        cb = self.get_callback(combo)
        if cb is not None:
            cb()
            return True
        return False

    def get_all_active_binds(self) -> Dict[KeyCombo, KeybindCallback]:
        """Return a dict of all currently active keybinds."""
        active = dict(self._base)
        for combo, stack in self._override_stacks.items():
            if stack:
                active[combo] = stack[-1]
        return active
