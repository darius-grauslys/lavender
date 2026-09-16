"""Tests for the client scanner (DebugClientScanner), its drivers, and the step
watchdog timeout normalization.

Run from repo root: python3 -m unittest mcp_layered.tests.test_client_scanner -v
Or:                 python3 mcp_layered/tests/test_client_scanner.py

The capture/advance (GDB I/O) is exercised against a mocked GDBSession whose
``-data-evaluate-expression`` / ``-interpreter-exec`` responses are driven by an
advance counter (like the process-pool tests) — no live GDB required.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_REPOS_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
sys.path.insert(0, _REPOS_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.debug_response import parse
from mcp_layered.layer_pygdbmi import GDBSession
from mcp_layered.debug_scanner_client import DebugClientScanner, _normalize_uuid
import mcp_layered.layer_lav_init as L


def _result_done(payload):
    """A raw (pygdbmi-format) ^done record."""
    return [{"type": "result", "message": "done", "payload": payload}]


def _make_gdb(write_side_effect):
    """A GDBSession over a mock controller whose write() uses the given
    side_effect (command -> response list)."""
    with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
        mock_gdb = MagicMock()
        mock_gdb.write.side_effect = write_side_effect
        mock_cls.return_value = mock_gdb
        return GDBSession()


def _client_struct(client_uuid=536870912, flags=1, center=(0, 63, 2),
                   client_count=1, out_count=1298,
                   out_kind="Game_Action_Kind__Global_Space__Store",
                   out_uuid=3601031185, in_count=0,
                   in_kind="Game_Action_Kind__None", in_uuid=0):
    """A realistic ``-data-evaluate-expression $debug_client_scanner`` printout.

    Uses %-formatting (not f-strings) so the literal ``{``/``}`` braces in the
    gdb struct printout are not treated as format fields. Braces are balanced so
    the scanner's nested-block extractor walks the right scope.
    """
    return (
        "$48 = {p_game = 0x5555556e4d50 <game>, "
        "p_client__current = 0x7fffdc3f3010, "
        "p_game_action__inbound__current = 0x7fffdc4f2a18, "
        "p_game_action__outbound__current = 0x7fffdc4f5220, "
        "m_refresh = 0x555555570a10 <__m_debug_client_scanner__refresh>, "
        "m_next_client = 0x555555570da0 <__m_debug_client_scanner__next_client>, "
        "m_next_game_action__inbound = 0x555555571030 <__m_debug_client_scanner__next_game_action__inbound>, "
        "m_next_game_action__outbound = 0x5555555710a0 <__m_debug_client_scanner__next_game_action__outbound>, "
        "quantity_of__clients = %d, "
        "game_actions = {"
        "quantity_of__game_actions__inbound = %d, "
        "game_action_header__inbound__current = "
        "{_serialiation_header = {size_of__struct = 0, uuid = %d}, "
        "the_kind_of_game_action__this_action_is = %s, game_action_flags = 0 '\\000'}, "
        "quantity_of__game_actions__outbound = %d, "
        "game_action_header__outbound__current = "
        "{_serialiation_header = {size_of__struct = 512, uuid = %d}, "
        "the_kind_of_game_action__this_action_is = %s, game_action_flags = 45 '-'}"
        "}, "
        "uuid_of__client__current = %d, "
        "current_client__local_space__center__3i32 = "
        "{x__i32 = %d, y__i32 = %d, z__i32 = %d}, "
        "current_client__client_flags__u16 = %d}"
    ) % (
        client_count,
        in_count, in_uuid, in_kind,
        out_count, out_uuid, out_kind,
        client_uuid,
        center[0], center[1], center[2],
        flags,
    )


def _empty_client_struct():
    """A scanner whose current client is unconnected (uuid sentinel, count 0)."""
    return _client_struct(
        client_count=0, client_uuid=4294967295, center=(-1, -1, -1), flags=0,
        out_count=0, out_kind="Game_Action_Kind__None", out_uuid=0,
        in_count=0, in_kind="Game_Action_Kind__None", in_uuid=0)


def _client_gdb(structs, advance_field):
    """A GDBSession whose ``-data-evaluate-expression $debug_client_scanner``
    returns ``structs[adv]`` where ``adv`` = the number of *advance_field*
    advances issued so far (cycling). The advance is the ``-interpreter-exec``
    whose text contains *advance_field*. This makes the initial get_scanner eval
    and the method's first eval agree (both at adv=0), matching real behavior."""
    state = {"adv": 0}

    def write(command, *a, **kw):
        if command.startswith("-interpreter-exec") and advance_field in command:
            state["adv"] += 1
            return _result_done({})
        if command == "-data-evaluate-expression $debug_client_scanner":
            return _result_done({"value": structs[state["adv"] % len(structs)]})
        return _result_done({})

    return _make_gdb(write)


class TestClientScannerList(unittest.TestCase):
    """Test DebugClientScanner.list_clients."""

    def test_single_client(self):
        gdb = _client_gdb([_client_struct(
            client_uuid=536870912, center=(0, 63, 2), flags=1)], "m_next_client")
        scanner = DebugClientScanner(gdb)
        result = scanner.list_clients()
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["declared"], 1)
        c = result["clients"][0]
        self.assertEqual(c["uuid"], "0x20000000")  # 536870912
        self.assertEqual(c["center"], {"x": 0, "y": 63, "z": 2})
        self.assertEqual(c["flags"], "1")

    def test_multiple_clients(self):
        structs = [
            _client_struct(client_uuid=536870912, center=(0, 63, 2)),
            _client_struct(client_uuid=536870913, center=(1, 0, 0)),
        ]
        gdb = _client_gdb(structs, "m_next_client")
        scanner = DebugClientScanner(gdb)
        result = scanner.list_clients()
        self.assertEqual(result["count"], 2)
        self.assertEqual(
            [c["uuid"] for c in result["clients"]],
            ["0x20000000", "0x20000001"])

    def test_no_clients(self):
        gdb = _client_gdb([_empty_client_struct()], "m_next_client")
        scanner = DebugClientScanner(gdb)
        result = scanner.list_clients()
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["declared"], 0)
        self.assertEqual(result["clients"], [])

    def test_unavailable_scanner(self):
        gdb = _make_gdb(lambda c, *a, **kw: [] if c.startswith("-data-evaluate")
                        else _result_done({}))
        scanner = DebugClientScanner(gdb)
        result = scanner.list_clients()
        self.assertIn("error", result)
        self.assertEqual(result["count"], 0)


class TestClientScannerActions(unittest.TestCase):
    """Test DebugClientScanner.scan_actions."""

    def test_outbound_full_tally(self):
        # Three distinct outbound actions (a full, small queue).
        structs = [
            _client_struct(out_count=3, out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=100),
            _client_struct(out_count=3, out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=101),
            _client_struct(out_count=3, out_kind="Game_Action_Kind__Global_Space__Request",
                           out_uuid=102),
        ]
        gdb = _client_gdb(structs, "m_next_game_action__outbound")
        scanner = DebugClientScanner(gdb)
        result = scanner.scan_actions("outbound")
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["tallied"], 3)
        self.assertTrue(result["complete"])
        self.assertEqual(result["by_kind"],
                         {"Game_Action_Kind__Global_Space__Store": 2,
                          "Game_Action_Kind__Global_Space__Request": 1})

    def test_outbound_partial_sample(self):
        # Declared total (10) exceeds the distinct structs (3); the walk wraps
        # after 3 and reports a partial sample.
        structs = [
            _client_struct(out_count=10, out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=100),
            _client_struct(out_count=10, out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=101),
            _client_struct(out_count=10, out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=102),
        ]
        gdb = _client_gdb(structs, "m_next_game_action__outbound")
        scanner = DebugClientScanner(gdb)
        result = scanner.scan_actions("outbound")
        self.assertEqual(result["total"], 10)
        self.assertEqual(result["tallied"], 3)
        self.assertFalse(result["complete"])
        self.assertEqual(result["by_kind"],
                         {"Game_Action_Kind__Global_Space__Store": 3})

    def test_skips_deallocated_current(self):
        # The first action is deallocated (sentinel uuid — a crashed/corrupted
        # state); the walk must skip it and still tally the live actions after it.
        structs = [
            _client_struct(out_count=5, out_kind="Game_Action_Kind__None",
                           out_uuid=0xFFFFFFFF),  # deallocated
            _client_struct(out_count=5,
                           out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=500),  # live
            _client_struct(out_count=5,
                           out_kind="Game_Action_Kind__Global_Space__Request",
                           out_uuid=501),  # live
        ]
        gdb = _client_gdb(structs, "m_next_game_action__outbound")
        scanner = DebugClientScanner(gdb)
        result = scanner.scan_actions("outbound")
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["tallied"], 2)
        self.assertEqual(result["by_kind"],
                         {"Game_Action_Kind__Global_Space__Store": 1,
                          "Game_Action_Kind__Global_Space__Request": 1})

    def test_max_iter_caps_walk(self):
        structs = [
            _client_struct(out_count=4, out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=100),
            _client_struct(out_count=4, out_kind="Game_Action_Kind__Global_Space__Request",
                           out_uuid=101),
            _client_struct(out_count=4, out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=102),
            _client_struct(out_count=4, out_kind="Game_Action_Kind__Global_Space__Request",
                           out_uuid=103),
        ]
        gdb = _client_gdb(structs, "m_next_game_action__outbound")
        scanner = DebugClientScanner(gdb)
        result = scanner.scan_actions("outbound", max_iter=2)
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["tallied"], 2)
        self.assertFalse(result["complete"])

    def test_inbound_direction(self):
        structs = [
            _client_struct(in_count=2, in_kind="Game_Action_Kind__World__Load_World",
                           in_uuid=200, out_count=0),
            _client_struct(in_count=2, in_kind="Game_Action_Kind__World__Load_Client",
                           in_uuid=201, out_count=0),
        ]
        gdb = _client_gdb(structs, "m_next_game_action__inbound")
        scanner = DebugClientScanner(gdb)
        result = scanner.scan_actions("inbound")
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["tallied"], 2)
        self.assertEqual(result["by_kind"],
                         {"Game_Action_Kind__World__Load_World": 1,
                          "Game_Action_Kind__World__Load_Client": 1})

    def test_empty_queue(self):
        structs = [_client_struct(out_count=0, out_kind="Game_Action_Kind__None",
                                  out_uuid=0)]
        gdb = _client_gdb(structs, "m_next_game_action__outbound")
        scanner = DebugClientScanner(gdb)
        result = scanner.scan_actions("outbound")
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["tallied"], 0)
        self.assertTrue(result["complete"])
        self.assertEqual(result["by_kind"], {})

    def test_bad_direction_errors(self):
        gdb = _client_gdb([_client_struct()], "m_next_game_action__outbound")
        scanner = DebugClientScanner(gdb)
        result = scanner.scan_actions("bogus")
        self.assertIn("error", result)


class TestClientDrivers(unittest.TestCase):
    """Test the client_list / client_actions scanner drivers."""

    def test_client_list_formats(self):
        gdb = _client_gdb([_client_struct(
            client_uuid=536870912, center=(0, 63, 2), flags=1)], "m_next_client")
        out = L.client_list_driver(gdb, MagicMock(), {})
        self.assertIn("Clients: 1 connected", out)
        self.assertIn("0x20000000", out)
        self.assertIn("(0,63,2)", out)

    def test_client_list_oob_center(self):
        # A client whose center is the OOB sentinel (BIT(31) signed per axis) is
        # not positioned yet; the driver reads it as such, not a coordinate.
        oob = -(1 << 31)
        gdb = _client_gdb([_client_struct(
            client_uuid=536870912, center=(oob, oob, oob), flags=1)],
            "m_next_client")
        out = L.client_list_driver(gdb, MagicMock(), {})
        self.assertIn("out of bounds / not positioned", out)

    def test_client_list_unavailable(self):
        gdb = _make_gdb(lambda c, *a, **kw: [] if c.startswith("-data-evaluate")
                        else _result_done({}))
        out = L.client_list_driver(gdb, MagicMock(), {})
        self.assertIn("ERROR", out)

    def test_client_list_gdb_closed(self):
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            gdb = GDBSession()
            gdb.close()
            out = L.client_list_driver(gdb, MagicMock(), {})
            self.assertIn("ERROR", out)
            self.assertIn("closed", out)
            gdb.close()

    def test_client_actions_formats(self):
        structs = [
            _client_struct(out_count=3,
                           out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=100),
            _client_struct(out_count=3,
                           out_kind="Game_Action_Kind__Global_Space__Store",
                           out_uuid=101),
            _client_struct(out_count=3,
                           out_kind="Game_Action_Kind__Global_Space__Request",
                           out_uuid=102),
        ]
        gdb = _client_gdb(structs, "m_next_game_action__outbound")
        out = L.client_actions_driver(gdb, MagicMock(), {})
        self.assertIn("outbound=3", out)
        self.assertIn("Global_Space__Store", out)
        self.assertIn("by Game_Action_Kind", out)

    def test_client_actions_bad_direction(self):
        gdb = _client_gdb([_client_struct()], "m_next_game_action__outbound")
        out = L.client_actions_driver(gdb, MagicMock(), {"direction": "bogus"})
        self.assertIn("ERROR", out)

    def test_client_actions_unavailable(self):
        gdb = _make_gdb(lambda c, *a, **kw: [] if c.startswith("-data-evaluate")
                        else _result_done({}))
        out = L.client_actions_driver(gdb, MagicMock(), {})
        self.assertIn("ERROR", out)


class TestNormalizeWatchdogTimeout(unittest.TestCase):
    """Test the step watchdog timeout normalization (negative -> unbounded)."""

    def test_negative_maps_to_unbounded(self):
        self.assertEqual(L._normalize_watchdog_timeout(-1), 0.0)
        self.assertEqual(L._normalize_watchdog_timeout(-30), 0.0)

    def test_zero_stays_zero(self):
        self.assertEqual(L._normalize_watchdog_timeout(0), 0.0)

    def test_positive_passes_through(self):
        self.assertEqual(L._normalize_watchdog_timeout(30), 30.0)
        self.assertEqual(L._normalize_watchdog_timeout(45.5), 45.5)

    def test_non_numeric_raises(self):
        with self.assertRaises(ValueError):
            L._normalize_watchdog_timeout("abc")
        with self.assertRaises(TypeError):
            L._normalize_watchdog_timeout(None)


class TestNormalizeUuid(unittest.TestCase):
    """Spot-check the uuid normalization used by the client scanner."""

    def test_decimal_to_hex(self):
        self.assertEqual(_normalize_uuid("536870912"), "0x20000000")

    def test_sentinel(self):
        self.assertEqual(_normalize_uuid("4294967295"), "(Identifier__u32)-1")

    def test_zero_is_none(self):
        self.assertIsNone(_normalize_uuid("0"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
