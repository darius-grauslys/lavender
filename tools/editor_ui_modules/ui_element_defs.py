"""Per-widget-type property schemas, defaults, and metadata.

Each definition describes:
* ``tag``            – XML tag name
* ``display_name``   – human-readable label
* ``supports_1x1``   – whether the tool can create a 1×1 tile element
* ``supports_nxn``   – whether the tool supports NxN drag-create
* ``default_attribs`` – dict of default XML attributes for a new element
* ``property_keys``  – ordered list of attribute keys shown in Properties HUD
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class UIElementDef:
    tag: str
    display_name: str
    supports_1x1: bool = True
    supports_nxn: bool = True
    has_ui_span: bool = True
    is_container: bool = False
    default_attribs: Dict[str, str] = field(default_factory=dict)
    property_keys: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Built-in definitions – one per widget in gen_ui_elements/widgets.py
# ---------------------------------------------------------------------------

BUTTON_DEF = UIElementDef(
    tag="button",
    display_name="Button",
    supports_1x1=True,
    supports_nxn=True,
    default_attribs={
        "x": "0", "y": "0", "width": "32", "height": "16",
        "m_Clicked_Handler": "m_ui_button__clicked_handler__default",
        "is_toggleable": "false",
        "is_toggled": "false",
        "color": "55,55,200",
    },
    property_keys=[
        "x", "y", "width", "height",
        "m_Clicked_Handler", "is_toggleable", "is_toggled",
        "text", "font_expression", "transform_handler",
        "color", "name", "UI_Span",
    ],
)

SLIDER_DEF = UIElementDef(
    tag="slider",
    display_name="Slider",
    supports_1x1=False,
    supports_nxn=True,
    default_attribs={
        "x": "0", "y": "0", "width": "64", "height": "8",
        "spanning_width": "64", "spanning_height": "8", "spanning_depth": "0",
        "m_Dragged_Handler": "m_ui_slider__dragged_handler__default",
        "snapped_x_or__y": "true",
        "span": "MISSING_FUNCTION_IN_XML",
        "size_of__texture": "8x8",
        "color": "55,200,55",
    },
    property_keys=[
        "x", "y", "width", "height",
        "spanning_width", "spanning_height", "spanning_depth",
        "m_Dragged_Handler", "snapped_x_or__y",
        "span", "size_of__texture", "name_of__texture",
        "index_of__sprite_frame", "color", "name", "UI_Span",
    ],
)

DRAGGABLE_DEF = UIElementDef(
    tag="draggable",
    display_name="Draggable",
    supports_1x1=True,
    supports_nxn=True,
    default_attribs={
        "x": "0", "y": "0", "width": "16", "height": "16",
        "m_Dragged_Handler": "m_ui_draggable__dragged_handler__default",
        "color": "200,200,55",
    },
    property_keys=[
        "x", "y", "width", "height",
        "m_Dragged_Handler", "color", "name", "UI_Span",
    ],
)

DROP_ZONE_DEF = UIElementDef(
    tag="drop_zone",
    display_name="Drop Zone",
    supports_1x1=True,
    supports_nxn=True,
    default_attribs={
        "x": "0", "y": "0", "width": "24", "height": "24",
        "m_Receive_Drop_Handler": "m_ui_drop_zone__receive_drop_handler__default",
        "color": "200,55,200",
    },
    property_keys=[
        "x", "y", "width", "height",
        "m_Receive_Drop_Handler", "color", "name", "UI_Span",
    ],
)

WINDOW_ELEMENT_DEF = UIElementDef(
    tag="window_element",
    display_name="Window Element",
    supports_1x1=False,
    supports_nxn=True,
    default_attribs={
        "x": "0", "y": "0", "width": "64", "height": "64",
        "window_kind": "Graphics_Window_Kind__Unknown",
        "offset_window__x": "0",
        "offset_window__y": "0",
        "offset_window__z": "0",
        "color": "55,200,200",
    },
    property_keys=[
        "x", "y", "width", "height",
        "window_kind",
        "offset_window__x", "offset_window__y", "offset_window__z",
        "layer", "text", "font_expression", "transform_handler",
        "color", "name",
    ],
)

BACKGROUND_DEF = UIElementDef(
    tag="background",
    display_name="Background",
    supports_1x1=False,
    supports_nxn=True,
    default_attribs={
        "x": "0", "y": "0", "width": "256", "height": "192",
        "p_gfx_window": "0",
        "color": "40,40,40",
    },
    property_keys=[
        "x", "y", "width", "height",
        "p_gfx_window", "color", "name", "UI_Span",
    ],
)

ALLOCATE_UI_DEF = UIElementDef(
    tag="allocate_ui",
    display_name="Alloc UI",
    supports_1x1=False,
    supports_nxn=False,
    has_ui_span=False,
    is_container=True,
    default_attribs={
        "x": "0", "y": "0",
        "color": "200,220,200",
    },
    property_keys=[
        "x", "y", "__width", "__height",
        "color", "name",
    ],
)

GROUP_DEF = UIElementDef(
    tag="group",
    display_name="Group",
    supports_1x1=False,
    supports_nxn=False,
    has_ui_span=False,
    is_container=True,
    default_attribs={
        "x": "0", "y": "0",
        "stride__x": "0", "stride__y": "0",
        "color": "220,220,220",
    },
    property_keys=[
        "x", "y", "stride__x", "stride__y",
        "__width", "__height",
        "color", "name",
    ],
)

GRID_DEF = UIElementDef(
    tag="grid",
    display_name="Grid",
    supports_1x1=False,
    supports_nxn=True,
    has_ui_span=False,
    is_container=True,
    default_attribs={
        "x": "0", "y": "0", "size": "1",
        "stride__x": "0", "stride__y": "0",
        "color": "200,200,200",
    },
    property_keys=[
        "x", "y", "size", "stride__x", "stride__y",
        "__width", "__height",
        "color", "name",
    ],
)

ALLOCATE_UI_CONTAINER_DEF = UIElementDef(
    tag="allocate_ui_container",
    display_name="Alloc Container",
    supports_1x1=False,
    supports_nxn=True,
    has_ui_span=False,
    is_container=True,
    default_attribs={
        "x": "0", "y": "0", "size": "1",
        "stride__x": "0", "stride__y": "0",
        "color": "180,180,180",
    },
    property_keys=[
        "x", "y", "size", "stride__x", "stride__y",
        "__width", "__height",
        "color", "name",
    ],
)

CODE_DEF = UIElementDef(
    tag="code",
    display_name="Code (raw)",
    supports_1x1=True,
    supports_nxn=False,
    has_ui_span=False,
    default_attribs={},
    property_keys=["name"],
)

# Master list
ALL_ELEMENT_DEFS: List[UIElementDef] = [
    BUTTON_DEF,
    SLIDER_DEF,
    DRAGGABLE_DEF,
    DROP_ZONE_DEF,
    WINDOW_ELEMENT_DEF,
    BACKGROUND_DEF,
    ALLOCATE_UI_DEF,
    GROUP_DEF,
    GRID_DEF,
    ALLOCATE_UI_CONTAINER_DEF,
    CODE_DEF,
]

ELEMENT_DEF_BY_TAG: Dict[str, UIElementDef] = {d.tag: d for d in ALL_ELEMENT_DEFS}
