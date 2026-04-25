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
from typing import Dict, List, Set

from keybinds.keybind import KeyCombo, KeybindCallback


class KeybindManager:
    """
    Manages keybinds with a stack-based override system.

    Base keybinds are used when the override stack is empty.
    Each push_override adds callbacks on top; pop_override
    removes the most recent push.
    """

    def __init__(self):
        self._base: Dict[KeyCombo, KeybindCallback] = {}
        # Per-key stack of override callbacks
        self._override_stacks: Dict[KeyCombo, List[KeybindCallback]] = \
            defaultdict(list)
        # Stack of key-sets pushed by each push_override call
        self._callee_override_stack: List[Set[KeyCombo]] = []

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
