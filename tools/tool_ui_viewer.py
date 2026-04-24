#!/usr/bin/env python3
"""tool_ui_viewer – pyglet-based live preview for gen_ui XML files.

Usage:
    python tools/tool_ui_viewer.py <source.xml> [config_field value ...]

The viewer watches the XML (and background images) for changes and
regenerates the C source on every save.
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Ensure repo root is importable
# ---------------------------------------------------------------------------
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_TOOLS_DIR)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import pyglet
from pyglet import image, shapes
from pyglet.gl import (
    GL_BLEND,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
    glBlendFunc,
    glEnable,
)

from tools.gen_ui import read_ui
from tools.gen_ui_elements.base import Background, Config

# ---------------------------------------------------------------------------
# Argument handling
# ---------------------------------------------------------------------------

if len(sys.argv) < 2:
    print("Usage: tool_ui_viewer.py <source.xml> [config_field value ...]")
    sys.exit(1)

_source_xml = sys.argv[1]
if not os.path.exists(_source_xml):
    print(f"Cannot find source xml: {_source_xml}")
    sys.exit(1)

config = Config(_source_xml)
config.is_visualizing = True

# Apply CLI overrides
_idx = 2
while _idx + 1 < len(sys.argv):
    _field = sys.argv[_idx]
    _value = sys.argv[_idx + 1]
    if hasattr(config, _field):
        current = getattr(config, _field)
        if isinstance(current, bool):
            setattr(config, _field, _value.lower() == "true")
        elif isinstance(current, int):
            setattr(config, _field, int(_value))
        else:
            setattr(config, _field, _value)
    else:
        print(f"warning: '{_field}' is not a valid config field")
    _idx += 2

# ---------------------------------------------------------------------------
# Window setup
# ---------------------------------------------------------------------------

window = pyglet.window.Window(
    width=config.window_size[0],
    height=config.window_size[1],
    visible=True,
)

_error_text: str = ""
_label_error = pyglet.text.Label(
    "",
    font_name="Times New Roman",
    font_size=36,
    x=0,
    y=0,
    width=config.window_size[0],
    height=36,
    color=(255, 55, 55, 255),
)

_modification_time: float = os.path.getmtime(config.source_xml)
_viewer_squares: list = []  # list of pyglet Rectangle shapes


def _resize_callback(size):
    window.set_size(size[0], size[1])


def _set_error(msg: str) -> None:
    global _error_text
    _error_text = msg


def _update_error_label(msg: str) -> None:
    global _label_error
    font_size = max(6, 1.5 * config.window_size[0] / (len(msg) + 1))
    _label_error = pyglet.text.Label(
        msg,
        font_name="Times New Roman",
        font_size=font_size,
        x=0,
        y=0,
        width=config.window_size[0],
        height=36,
        color=(255, 55, 55, 255),
    )


def _get_y(y, height):
    return window.height - y - height


# ---------------------------------------------------------------------------
# Background image loading (with magenta-key transparency)
# ---------------------------------------------------------------------------

def _load_background_image(bg: Background) -> None:
    """Load the background image and apply magenta-key transparency."""
    if not bg.path:
        bg.image = None
        return
    try:
        bg.image = image.load(bg.path)
    except Exception:
        bg.image = None
        return
    raw = bg.image.get_image_data()
    fmt = "RGBA"
    pitch = raw.width * len(fmt)
    pixels = bytearray(raw.get_data(fmt, pitch))
    for i in range(len(pixels) // 4):
        if pixels[i * 4] == 0xFF and pixels[i * 4 + 2] == 0xFF:
            pixels[i * 4 + 3] = 0x00
        else:
            pixels[i * 4 + 3] = 0xFF
    raw.set_data(fmt, pitch, bytes(pixels))


# Pre-load existing backgrounds
for _bg in config.backgrounds:
    _load_background_image(_bg)


# ---------------------------------------------------------------------------
# Regeneration helper
# ---------------------------------------------------------------------------

def _regenerate() -> None:
    global _viewer_squares
    _viewer_squares.clear()
    state = read_ui(
        config.source_xml,
        config,
        resize_callback=_resize_callback,
    )
    if state is None:
        _set_error("Generation failed – see console.")
        return
    _set_error("")
    # Convert abstract square tuples into pyglet shapes
    for x, y, w, h, color in state.squares:
        _viewer_squares.append(
            shapes.Rectangle(
                x=x,
                y=_get_y(y, h),
                width=w,
                height=h,
                color=color,
            )
        )


# ---------------------------------------------------------------------------
# Draw loop
# ---------------------------------------------------------------------------

@window.event
def on_draw():
    global _modification_time, _error_text

    window.clear()
    glEnable(GL_BLEND)

    if _error_text:
        _update_error_label(_error_text)
        _error_text = ""

    # Check for XML changes
    new_mtime = (
        os.path.getmtime(config.source_xml)
        if os.path.exists(config.source_xml)
        else 0
    )
    if _modification_time < new_mtime:
        _modification_time = new_mtime
        _regenerate()

    # Check for background image changes
    for i, bg in enumerate(config.backgrounds):
        if not bg.path:
            continue
        new_mt = (
            os.path.getmtime(bg.path) if os.path.exists(bg.path) else 0
        )
        if bg.modification_time < new_mt:
            full_path = os.path.join(config.base_dir, bg.path)
            config.backgrounds[i] = Background(
                full_path,
                bg.layer,
                config.backgrounds[i].x,
                config.backgrounds[i].y,
            )
            _load_background_image(config.backgrounds[i])

        if bg.image is not None:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            bg.image.blit(
                bg.x,
                window.height - bg.y - bg.image.height,
                0,
            )

    for sq in _viewer_squares:
        sq.draw()

    if _label_error.text:
        _label_error.x = config.window_size[0] / 2 - _label_error.width / 3
        _label_error.y = config.window_size[1] / 2 - _label_error.height / 2
        _label_error.draw()


# ---------------------------------------------------------------------------
# Initial generation + main loop
# ---------------------------------------------------------------------------

_regenerate()
pyglet.app.run()
