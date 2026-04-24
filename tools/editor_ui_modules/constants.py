"""Shared constants for the UI editor."""

# Grid
GRID_PX = 8

# History
HISTORY_MAX = 128

# Selection outline
OUTLINE_WIDTH = 3
COLOR_OUTLINE_SELECTED = (0.6, 0.0, 0.8, 1.0)      # purple
COLOR_OUTLINE_FOCUSED  = (1.0, 0.0, 0.0, 1.0)       # bright red
COLOR_OUTLINE_REVEAL   = (0.6, 0.0, 0.8, 0.7)       # purple semi

# Delete button
COLOR_DELETE_X = (1.0, 0.2, 0.2, 1.0)

# Message HUD
COLOR_MSG_INFO_TEXT  = (0.0, 0.0, 0.0, 1.0)
COLOR_MSG_ERROR_BG   = (0.4, 0.0, 0.0, 1.0)
COLOR_MSG_ERROR_TEXT  = (1.0, 1.0, 1.0, 1.0)

# Default window
DEFAULT_WINDOW_W = 800
DEFAULT_WINDOW_H = 600

# Work area defaults
DEFAULT_WORK_W = 256
DEFAULT_WORK_H = 192

# Tools JSON path (relative to assets/ui)
TOOLS_JSON_RELPATH = "tools.json"

# Asset root (relative to project root / cwd)
ASSET_UI_ROOT = "assets/ui"
