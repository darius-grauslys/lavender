"""Left-hand collapsible file-tree HUD rooted at assets/ui."""

from __future__ import annotations

import os
from typing import Callable, Optional

import imgui

from tools.editor_ui_modules.constants import ASSET_UI_ROOT


class FileBrowser:
    """Renders a recursive directory tree and reports clicks."""

    def __init__(self, root_dir: str = ASSET_UI_ROOT):
        self.root_dir = root_dir
        self.selected_path: Optional[str] = None
        self._expanded: dict[str, bool] = {}

    # ------------------------------------------------------------------
    def draw(
        self,
        on_select_xml: Callable[[str], None],
        on_select_png: Callable[[str], None],
        width: float = 200,
    ) -> None:
        """Standalone draw (creates its own window). Used if not embedded."""
        imgui.set_next_window_size(width, 0)
        imgui.set_next_window_position(0, 0, condition=imgui.FIRST_USE_EVER)

        expanded, opened = imgui.begin(
            "Files##file_browser",
            closable=False,
            flags=(
                imgui.WINDOW_NO_MOVE
                | imgui.WINDOW_ALWAYS_AUTO_RESIZE
            ),
        )
        if expanded:
            if os.path.isdir(self.root_dir):
                self._draw_dir(self.root_dir, on_select_xml, on_select_png)
            else:
                imgui.text_colored("(missing assets/ui)", 1, 0.3, 0.3)
        imgui.end()

    # ------------------------------------------------------------------
    def _draw_dir(
        self,
        dirpath: str,
        on_xml: Callable[[str], None],
        on_png: Callable[[str], None],
    ) -> None:
        try:
            entries = sorted(os.listdir(dirpath))
        except OSError:
            return

        dirs = [e for e in entries if os.path.isdir(os.path.join(dirpath, e))]
        files = [e for e in entries if os.path.isfile(os.path.join(dirpath, e))]

        for d in dirs:
            full = os.path.join(dirpath, d)
            node_open = imgui.tree_node(
                f"{d}##{full}",
                imgui.TREE_NODE_OPEN_ON_ARROW,
            )
            if node_open:
                self._draw_dir(full, on_xml, on_png)
                imgui.tree_pop()

        for f in files:
            full = os.path.join(dirpath, f)
            is_selected = self.selected_path == full
            clicked, _ = imgui.selectable(
                f"  {f}##{full}", is_selected
            )
            if clicked:
                self.selected_path = full
                if f.lower().endswith(".xml"):
                    on_xml(full)
                elif f.lower().endswith(".png"):
                    on_png(full)
