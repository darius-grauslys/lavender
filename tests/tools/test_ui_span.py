"""
Tests for UI_Span parsing and C code emission in tools/gen_ui_code.py.

Covers two functions:
  - parse_ui_span(raw): parses a UI_Span attribute string into (size, [9 ints])
  - _emit_tile_span_from_indices(state, name, size, indices): emits C code that
    declares and initialises a UI_Tile_Span with the correct corner/edge/fill
    mapping and registers it on the UI element.
"""

from __future__ import annotations

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.gen_ui_code import parse_ui_span, _emit_tile_span_from_indices, CodeWriter


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

class MockCtx:
    def __init__(self, p_ui_element: str = "p_ui_iterator"):
        self.p_ui_element = p_ui_element


class MockState:
    def __init__(self, p_ui_element: str = "p_ui_iterator"):
        self.writer = CodeWriter()
        self.ctx = MockCtx(p_ui_element)


# ---------------------------------------------------------------------------
# TestParseUISpan
# ---------------------------------------------------------------------------

class TestParseUISpan(unittest.TestCase):
    """Tests for parse_ui_span()."""

    # --- Happy path ---

    def test_parse_basic_size_1(self):
        result = parse_ui_span("1;0,1,2,3,4,5,6,7,8")
        self.assertEqual(result, (1, [0, 1, 2, 3, 4, 5, 6, 7, 8]))

    def test_parse_size_2(self):
        result = parse_ui_span("2;0,2,4,32,34,36,64,66,68")
        self.assertEqual(result, (2, [0, 2, 4, 32, 34, 36, 64, 66, 68]))

    def test_parse_large_size(self):
        result = parse_ui_span("4;10,20,30,40,50,60,70,80,90")
        self.assertEqual(result, (4, [10, 20, 30, 40, 50, 60, 70, 80, 90]))

    def test_parse_multi_state_returns_first(self):
        result = parse_ui_span("1;0,1,2,3,4,5,6,7,8;10,11,12,13,14,15,16,17,18")
        self.assertEqual(result, (1, [0, 1, 2, 3, 4, 5, 6, 7, 8]))

    def test_parse_multi_state_size_2(self):
        result = parse_ui_span("2;0,2,4,32,34,36,64,66,68;100,102,104,132,134,136,164,166,168")
        self.assertEqual(result, (2, [0, 2, 4, 32, 34, 36, 64, 66, 68]))

    def test_parse_whitespace_tolerance(self):
        result = parse_ui_span(" 1 ; 0 , 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 ")
        self.assertEqual(result, (1, [0, 1, 2, 3, 4, 5, 6, 7, 8]))

    def test_parse_zero_indices(self):
        result = parse_ui_span("1;0,0,0,0,0,0,0,0,0")
        self.assertEqual(result, (1, [0, 0, 0, 0, 0, 0, 0, 0, 0]))

    def test_parse_max_tile_kind_indices(self):
        result = parse_ui_span("1;1023,1023,1023,1023,1023,1023,1023,1023,1023")
        self.assertEqual(result, (1, [1023] * 9))

    # --- Corner cases / aggressive assertions ---

    def test_parse_empty_string(self):
        result = parse_ui_span("")
        self.assertIsNone(result)

    def test_parse_none_like_empty(self):
        # Whitespace-only string: after strip the first segment is empty.
        # The parser calls int("") which raises ValueError, or returns None.
        # Either is acceptable — document that it does not return a valid tuple.
        try:
            result = parse_ui_span("   ")
            self.assertIsNone(result)
        except ValueError:
            pass  # ValueError is also acceptable behaviour

    def test_parse_missing_tiles_after_size(self):
        # Size only, no tile data segment → tile_seg is "" → split gives [""]
        # int("") raises ValueError, which propagates upward.
        with self.assertRaises((ValueError, TypeError)):
            parse_ui_span("2")

    def test_parse_wrong_count_too_few(self):
        result = parse_ui_span("1;0,1,2,3,4,5,6,7")
        self.assertIsNone(result)

    def test_parse_wrong_count_too_many(self):
        result = parse_ui_span("1;0,1,2,3,4,5,6,7,8,9")
        self.assertIsNone(result)

    def test_parse_non_numeric_size(self):
        # Non-numeric first segment without commas → int() raises ValueError.
        with self.assertRaises(ValueError):
            parse_ui_span("abc;0,1,2,3,4,5,6,7,8")

    def test_parse_non_numeric_tile(self):
        # Non-numeric tile value → int() raises ValueError.
        with self.assertRaises(ValueError):
            parse_ui_span("1;0,1,x,3,4,5,6,7,8")

    def test_parse_negative_tile_index(self):
        # The parser does not reject negative values; the C cast handles semantics.
        result = parse_ui_span("1;-1,1,2,3,4,5,6,7,8")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1][0], -1)

    def test_parse_size_zero(self):
        # Parser does not validate size semantics; size=0 is returned as-is.
        result = parse_ui_span("0;0,1,2,3,4,5,6,7,8")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], [0, 1, 2, 3, 4, 5, 6, 7, 8])

    def test_parse_comma_in_first_segment_legacy(self):
        # When the first segment contains commas there is no explicit size prefix.
        # The parser treats this as size=1 with that segment as the tile data.
        result = parse_ui_span("0,1,2,3,4,5,6,7,8")
        self.assertEqual(result, (1, [0, 1, 2, 3, 4, 5, 6, 7, 8]))


# ---------------------------------------------------------------------------
# TestEmitTileSpanFromIndices
# ---------------------------------------------------------------------------

class TestEmitTileSpanFromIndices(unittest.TestCase):
    """Tests for _emit_tile_span_from_indices()."""

    def _call(self, size, indices, p_ui_element="p_ui_iterator"):
        state = MockState(p_ui_element)
        _emit_tile_span_from_indices(state, state.ctx.p_ui_element, size, indices)
        return state.writer.get_source()

    # --- Happy path ---

    def test_emit_size_1_basic(self):
        src = self._call(1, [0, 1, 2, 3, 4, 5, 6, 7, 8])

        # Variable declarations
        self.assertIn("UI_Tile_Span ui_tile_span__p_ui_iterator;", src)
        self.assertIn("UI_Tile corners__p_ui_iterator[4];", src)
        self.assertIn("UI_Tile edges__p_ui_iterator[4];", src)
        self.assertIn("UI_Tile fill__p_ui_iterator;", src)

        # Corner mapping: TL=0, TR=2, BL=6, BR=8
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[0], (UI_Tile_Kind)0, UI_TILE_FLAGS__NONE);", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[1], (UI_Tile_Kind)2, UI_TILE_FLAGS__NONE);", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[2], (UI_Tile_Kind)6, UI_TILE_FLAGS__NONE);", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[3], (UI_Tile_Kind)8, UI_TILE_FLAGS__NONE);", src)

        # Edge mapping: T=1, R=5, B=7, L=3
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[0], (UI_Tile_Kind)1, UI_TILE_FLAGS__NONE);", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[1], (UI_Tile_Kind)5, UI_TILE_FLAGS__NONE);", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[2], (UI_Tile_Kind)7, UI_TILE_FLAGS__NONE);", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[3], (UI_Tile_Kind)3, UI_TILE_FLAGS__NONE);", src)

        # Fill: M=4
        self.assertIn("initialize_ui_tile(&fill__p_ui_iterator, (UI_Tile_Kind)4, UI_TILE_FLAGS__NONE);", src)

        # Span initialisation (size==1 → plain variant, NOT __with_ui_tile_size)
        self.assertIn(
            "initialize_ui_tile_span(&ui_tile_span__p_ui_iterator, corners__p_ui_iterator, "
            "edges__p_ui_iterator, fill__p_ui_iterator);",
            src,
        )

        # Registration
        self.assertIn(
            "set_ui_tile_span_of__ui_element(p_ui_iterator, &ui_tile_span__p_ui_iterator);",
            src,
        )

    def test_emit_size_2_uses_with_size_variant(self):
        indices = [0, 2, 4, 32, 34, 36, 64, 66, 68]
        src = self._call(2, indices)

        # Must use the __with_ui_tile_size variant
        self.assertIn("initialize_ui_tile_span__with_ui_tile_size", src)
        # Must NOT use the plain variant for the span init
        self.assertNotIn(
            "initialize_ui_tile_span(&ui_tile_span__p_ui_iterator,",
            src,
        )

        # Size argument "2" must appear in the call
        self.assertIn("2", src)

        # Corner mapping: TL=0, TR=4, BL=64, BR=68
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[0], (UI_Tile_Kind)0,", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[1], (UI_Tile_Kind)4,", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[2], (UI_Tile_Kind)64,", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[3], (UI_Tile_Kind)68,", src)

        # Edge mapping: T=2, R=36, B=66, L=32
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[0], (UI_Tile_Kind)2,", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[1], (UI_Tile_Kind)36,", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[2], (UI_Tile_Kind)66,", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[3], (UI_Tile_Kind)32,", src)

        # Fill: M=34
        self.assertIn("initialize_ui_tile(&fill__p_ui_iterator, (UI_Tile_Kind)34,", src)

    def test_emit_index_mapping_correctness(self):
        # Distinctive non-overlapping values make index swaps immediately visible.
        indices = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        src = self._call(1, indices)

        # corners: TL=10, TR=30, BL=70, BR=90
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[0], (UI_Tile_Kind)10,", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[1], (UI_Tile_Kind)30,", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[2], (UI_Tile_Kind)70,", src)
        self.assertIn("initialize_ui_tile(&corners__p_ui_iterator[3], (UI_Tile_Kind)90,", src)

        # edges: T=20, R=60, B=80, L=40
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[0], (UI_Tile_Kind)20,", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[1], (UI_Tile_Kind)60,", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[2], (UI_Tile_Kind)80,", src)
        self.assertIn("initialize_ui_tile(&edges__p_ui_iterator[3], (UI_Tile_Kind)40,", src)

        # fill: M=50
        self.assertIn("initialize_ui_tile(&fill__p_ui_iterator, (UI_Tile_Kind)50,", src)

    def test_emit_custom_element_name(self):
        src = self._call(1, [0, 1, 2, 3, 4, 5, 6, 7, 8], p_ui_element="p_my_button")

        self.assertIn("UI_Tile_Span ui_tile_span__p_my_button;", src)
        self.assertIn("UI_Tile corners__p_my_button[4];", src)
        self.assertIn("UI_Tile edges__p_my_button[4];", src)
        self.assertIn("UI_Tile fill__p_my_button;", src)
        self.assertIn("initialize_ui_tile(&corners__p_my_button[0],", src)
        self.assertIn("initialize_ui_tile(&edges__p_my_button[0],", src)
        self.assertIn("initialize_ui_tile(&fill__p_my_button,", src)
        self.assertIn("set_ui_tile_span_of__ui_element(p_my_button, &ui_tile_span__p_my_button);", src)

        # Ensure the old name does not bleed in
        self.assertNotIn("p_ui_iterator", src)

    def test_emit_large_tile_kinds(self):
        indices = [1023, 512, 256, 128, 64, 32, 16, 8, 4]
        src = self._call(1, indices)

        # TL=1023 → corners[0], TR=256 → corners[1], BL=16 → corners[2], BR=4 → corners[3]
        self.assertIn("(UI_Tile_Kind)1023", src)
        self.assertIn("(UI_Tile_Kind)256", src)
        self.assertIn("(UI_Tile_Kind)16", src)
        self.assertIn("(UI_Tile_Kind)4", src)

    def test_emit_all_same_indices(self):
        src = self._call(1, [5, 5, 5, 5, 5, 5, 5, 5, 5])

        # Every tile init should use kind 5
        import re
        kinds = re.findall(r'\(UI_Tile_Kind\)(\d+)', src)
        self.assertEqual(len(kinds), 9, f"Expected 9 initialize_ui_tile calls, found: {kinds}")
        self.assertTrue(all(k == '5' for k in kinds), f"Expected all kind=5, got: {kinds}")

    def test_emit_size_1_does_not_contain_with_size(self):
        src = self._call(1, [0, 1, 2, 3, 4, 5, 6, 7, 8])
        self.assertNotIn("initialize_ui_tile_span__with_ui_tile_size", src)

    def test_emit_size_3_uses_with_size_variant(self):
        src = self._call(3, [0, 1, 2, 3, 4, 5, 6, 7, 8])

        self.assertIn("initialize_ui_tile_span__with_ui_tile_size", src)
        # "3" must appear as the final argument in that call
        import re
        match = re.search(
            r'initialize_ui_tile_span__with_ui_tile_size\([^)]*,\s*(\d+)\)',
            src,
        )
        self.assertIsNotNone(match, "Could not find __with_ui_tile_size call with a trailing size arg")
        self.assertEqual(match.group(1), "3")

    def test_emit_declaration_order(self):
        src = self._call(1, [0, 1, 2, 3, 4, 5, 6, 7, 8])

        decl_pos = src.index("UI_Tile_Span")
        init_pos = src.index("initialize_ui_tile(")
        self.assertLess(
            decl_pos,
            init_pos,
            "Variable declarations must appear before initialize_ui_tile calls",
        )

    def test_emit_registration_is_last(self):
        src = self._call(1, [0, 1, 2, 3, 4, 5, 6, 7, 8])

        reg_pos = src.index("set_ui_tile_span_of__ui_element")
        span_init_pos = src.index("initialize_ui_tile_span(")
        self.assertGreater(
            reg_pos,
            span_init_pos,
            "set_ui_tile_span_of__ui_element must come after the span initializer",
        )

        # Verify it is truly the last function call (nothing after it except
        # possible whitespace).
        after_reg = src[reg_pos:].strip()
        # The registration line itself should be the last non-empty content.
        lines_after = [l.strip() for l in after_reg.splitlines() if l.strip()]
        self.assertEqual(
            lines_after[0],
            "set_ui_tile_span_of__ui_element(p_ui_iterator, &ui_tile_span__p_ui_iterator);",
        )
        self.assertEqual(len(lines_after), 1, f"Expected no output after registration, got: {lines_after[1:]}")


if __name__ == "__main__":
    unittest.main()
