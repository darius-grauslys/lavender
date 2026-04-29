"""test_mcp_transport.py — Verify the FastMCP server's tool registry.

Directly inspects the FastMCP instance's internal tool manager to confirm:
  - Exactly 28 tools are registered (13 scripts, 28 tools total).
  - Each expected tool name is present.
  - Every tool has a non-empty description.
"""

import sys
from pathlib import Path

import pytest

# Ensure the tools/ directory is importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lav_ai.lav_ai_app import mcp as lavender_mcp

# ---------------------------------------------------------------------------
# Expected tool names
# ---------------------------------------------------------------------------

EXPECTED_TOOL_NAMES = {
    "gen_ui_code",
    "gen_ui_create",
    "gen_game_action",
    "gen_sprite_kind",
    "gen_sprite_animation",
    "gen_sprite_animation_group",
    "gen_png",
    "gen_tile",
    "gen_tile_layer_name",
    "gen_tile_layer_make_default",
    "gen_entity",
    "gen_ui_tile_kind",
    "read_png_meta",
    "read_png",
    "mod_png_set",
    "mod_png_swap",
    "mod_png_copy",
    "mod_png_resize",
    "mod_png_condense",
    "gen_aliased_texture",
    "query_tools_list",
    "query_tools_search",
    "query_tools_describe",
    "query_agents_list",
    "query_agents_show",
    "query_agents_search_prompts",
    "query_agents_search_permissions",
    "query_agents_verify_clean",
}

EXPECTED_TOOL_COUNT = 28


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_tools() -> dict:
    """Return the internal tools dict from the FastMCP tool manager."""
    return lavender_mcp._tool_manager._tools


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMcpToolRegistry:
    def test_tool_count(self):
        """The server must expose exactly the expected number of tools."""
        tools = _get_tools()
        assert len(tools) == EXPECTED_TOOL_COUNT, (
            f"Expected {EXPECTED_TOOL_COUNT} tools, "
            f"got {len(tools)}: {sorted(tools.keys())}"
        )

    @pytest.mark.parametrize("tool_name", sorted(EXPECTED_TOOL_NAMES))
    def test_tool_is_registered(self, tool_name):
        """Every expected tool name must be present in the registry."""
        tools = _get_tools()
        assert tool_name in tools, (
            f"Tool '{tool_name}' not found. "
            f"Registered tools: {sorted(tools.keys())}"
        )

    @pytest.mark.parametrize("tool_name", sorted(EXPECTED_TOOL_NAMES))
    def test_tool_has_description(self, tool_name):
        """Every registered tool must have a non-empty description."""
        tools = _get_tools()
        if tool_name not in tools:
            pytest.skip(f"Tool '{tool_name}' not registered")
        tool = tools[tool_name]
        description = tool.description
        assert description and description.strip(), (
            f"Tool '{tool_name}' has an empty description"
        )
