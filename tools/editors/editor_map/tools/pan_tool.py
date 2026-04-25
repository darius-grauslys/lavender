"""
Base panning tool (spec section 1.1 — Panning Tool).

Default keybind overrides when active:
- Scroll wheel (no modifier): vertical panning
- Shift + Scroll wheel: horizontal panning
- Alt + Scroll wheel: zoom in/out
- Arrow keys: move by 1 tile
"""

from __future__ import annotations

from typing import Dict, Optional

from tools.tool import Tool
from keybinds.keybind import (
    KeyCombo, KeybindCallback, Modifier,
    VIRTUAL_KEY_SCROLL_UP, VIRTUAL_KEY_SCROLL_DOWN,
    VIRTUAL_KEY_ZOOM_IN, VIRTUAL_KEY_ZOOM_OUT,
)
from keybinds.keybind_manager import KeybindManager
from workspace.movement import WorkspaceMovement

# GLFW arrow key constants (duplicated here to avoid a hard
# dependency on glfw at import time — values are stable).
_KEY_UP = 265
_KEY_DOWN = 264
_KEY_LEFT = 263
_KEY_RIGHT = 262


class PanTool(Tool):
    """Base pan tool — moves the workspace viewport.

    Subclasses override ``_build_keybinds`` to customise which
    movement callbacks are registered (e.g. chunk-level vs
    tile-level arrow keys, shift+arrow for chunk/global-space).
    """

    name = "Pan"
    icon_label = "P"

    def __init__(self, movement: Optional[WorkspaceMovement] = None):
        self._is_active: bool = False
        self._movement: Optional[WorkspaceMovement] = movement

    def set_movement(self, movement: WorkspaceMovement) -> None:
        """Inject the workspace movement controller."""
        self._movement = movement

    # ------------------------------------------------------------------
    # Keybind construction — override in subclasses for mode-specific
    # arrow-key behaviour.
    # ------------------------------------------------------------------

    def _build_keybinds(self) -> Dict[KeyCombo, KeybindCallback]:
        """Return the keybind overrides for this pan tool.

        The base implementation provides:
        - Arrow keys → pan by 1 tile
        - Scroll up/down (no mod) → vertical pan
        - Scroll up/down (shift) → horizontal pan
        - Zoom in/out (alt) → zoom
        """
        if self._movement is None:
            return {}

        m = self._movement
        binds: Dict[KeyCombo, KeybindCallback] = {
            # Arrow keys — 1 tile
            KeyCombo(_KEY_UP, Modifier.NONE): m.make_pan_tile_up(),
            KeyCombo(_KEY_DOWN, Modifier.NONE): m.make_pan_tile_down(),
            KeyCombo(_KEY_LEFT, Modifier.NONE): m.make_pan_tile_left(),
            KeyCombo(_KEY_RIGHT, Modifier.NONE): m.make_pan_tile_right(),
            # Scroll wheel — vertical pan
            KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.NONE):
                m.make_scroll_up(),
            KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.NONE):
                m.make_scroll_down(),
            # Shift + scroll — horizontal pan
            KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.SHIFT):
                m.make_scroll_left(),
            KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.SHIFT):
                m.make_scroll_right(),
            # Alt + scroll — zoom
            KeyCombo(VIRTUAL_KEY_ZOOM_IN, Modifier.ALT):
                m.make_zoom_in(),
            KeyCombo(VIRTUAL_KEY_ZOOM_OUT, Modifier.ALT):
                m.make_zoom_out(),
        }
        return binds

    # ------------------------------------------------------------------
    # Activation / deactivation
    # ------------------------------------------------------------------

    def on_activate(self, keybind_manager: KeybindManager) -> None:
        """Push pan keybind overrides."""
        super().on_activate(keybind_manager)
        self._is_active = True
        keybind_manager.push_override(self._build_keybinds())

    def on_deactivate(self, keybind_manager=None) -> None:
        """Pop pan keybind overrides."""
        self._is_active = False
        if keybind_manager is not None:
            keybind_manager.pop_override()

    def on_workspace_drag(self, dx: float, dy: float) -> None:
        """Pan is handled by the workspace movement system."""
        if self._movement is not None:
            self._movement.pan_by_pixels(dx, dy)
