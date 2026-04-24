"""Top-right TOOL HUD – tool palette and UI-span configuration.

Reads / writes ``tools.json`` from the assets/ui directory.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

import imgui

from tools.editor_ui_modules.constants import ASSET_UI_ROOT, GRID_PX, TOOLS_JSON_RELPATH
from tools.editor_ui_modules.ui_element_defs import (
    ALL_ELEMENT_DEFS,
    UIElementDef,
)


class ToolSpanConfig:
    """Persisted span configuration for one tool."""

    def __init__(
        self,
        supports_1x1: bool = False,
        supports_nxn: bool = False,
        span_1x1_index: int = 0,
        span_9_indices: Optional[List[int]] = None,
    ):
        self.supports_1x1 = supports_1x1
        self.supports_nxn = supports_nxn
        self.span_1x1_index = span_1x1_index
        self.span_9_indices = span_9_indices if span_9_indices is not None else [0] * 9

    def to_dict(self) -> dict:
        return {
            "supports_1x1": self.supports_1x1,
            "supports_nxn": self.supports_nxn,
            "span_1x1_index": self.span_1x1_index,
            "span_9_indices": list(self.span_9_indices),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ToolSpanConfig":
        return cls(
            supports_1x1=d.get("supports_1x1", False),
            supports_nxn=d.get("supports_nxn", False),
            span_1x1_index=d.get("span_1x1_index", 0),
            span_9_indices=d.get("span_9_indices", [0] * 9),
        )


class ToolHUD:
    """Top-right tool palette."""

    def __init__(self):
        self.selected_tool: Optional[UIElementDef] = None
        self._span_configs: Dict[str, ToolSpanConfig] = {}
        self._load_tools_json()
        # Ensure every known element def has a config entry
        for edef in ALL_ELEMENT_DEFS:
            if edef.tag not in self._span_configs:
                self._span_configs[edef.tag] = ToolSpanConfig(
                    supports_1x1=edef.supports_1x1,
                    supports_nxn=edef.supports_nxn,
                )

    # -- persistence -------------------------------------------------------

    def _json_path(self) -> str:
        return os.path.join(ASSET_UI_ROOT, TOOLS_JSON_RELPATH)

    def _load_tools_json(self) -> None:
        path = self._json_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for tag, cfg_dict in data.items():
                self._span_configs[tag] = ToolSpanConfig.from_dict(cfg_dict)
        except (json.JSONDecodeError, OSError):
            pass

    def _save_tools_json(self) -> None:
        path = self._json_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {tag: cfg.to_dict() for tag, cfg in self._span_configs.items()}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    # -- accessors ---------------------------------------------------------

    def get_span_config(self, tag: str) -> ToolSpanConfig:
        return self._span_configs.get(tag, ToolSpanConfig())

    # -- drawing -----------------------------------------------------------

    def draw(
        self,
        window_width: float,
        window_height: float,
        panel_width: float = 220,
    ) -> Optional[UIElementDef]:
        """Draw the tool palette.  Returns the currently selected tool def."""
        half_h = window_height * 0.5
        imgui.set_next_window_position(window_width - panel_width, 0)
        imgui.set_next_window_size(panel_width, half_h)

        flags = (
            imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("Tools##tool_hud", closable=False, flags=flags)

        imgui.text("Select a tool:")
        imgui.separator()

        for edef in ALL_ELEMENT_DEFS:
            is_sel = self.selected_tool is edef
            if imgui.selectable(
                f"{edef.display_name}##{edef.tag}", is_sel
            )[0]:
                self.selected_tool = edef

        imgui.separator()

        # Span config for selected tool
        if self.selected_tool is not None:
            tag = self.selected_tool.tag
            cfg = self._span_configs.setdefault(tag, ToolSpanConfig())
            changed = False

            imgui.text(f"Span config: {self.selected_tool.display_name}")

            c1, cfg.supports_1x1 = imgui.checkbox("1x1 support", cfg.supports_1x1)
            changed = changed or c1
            c2, cfg.supports_nxn = imgui.checkbox("NxN support", cfg.supports_nxn)
            changed = changed or c2

            if cfg.supports_1x1:
                imgui.text("1x1 tile index:")
                c3, cfg.span_1x1_index = imgui.input_int(
                    "##1x1idx", cfg.span_1x1_index
                )
                changed = changed or c3

            if cfg.supports_nxn:
                imgui.text("9-slice indices:")
                labels = [
                    "TL", "T", "TR",
                    "L", "C", "R",
                    "BL", "B", "BR",
                ]
                for i, label in enumerate(labels):
                    if i % 3 != 0:
                        imgui.same_line()
                    ci, cfg.span_9_indices[i] = imgui.input_int(
                        f"##{label}_{tag}", cfg.span_9_indices[i]
                    )
                    changed = changed or ci

            if changed:
                self._save_tools_json()

        imgui.end()
        return self.selected_tool
