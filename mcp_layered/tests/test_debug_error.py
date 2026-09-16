"""Tests for debug_error module."""

import os
import sys
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.debug_error import (
    parse_backtrace,
    find_debug_error_frame,
    adjust_frame_for_debug_error,
    format_arguments_for_frame,
)


class TestParseBacktrace(unittest.TestCase):
    """Tests for parse_backtrace function."""

    def test_parse_simple_backtrace(self):
        """parse_backtrace extracts frames from a standard backtrace string."""
        bt = """#0 abort at stdlib/abort.c:73
#1 raise at sysdeps/posix/raise.c:26
#2 main at main.c:10"""

        frames = parse_backtrace(bt)
        self.assertEqual(len(frames), 3)
        self.assertEqual(frames[0]['func'], 'abort')
        self.assertEqual(frames[0]['line'], '73')
        self.assertEqual(frames[1]['func'], 'raise')
        self.assertEqual(frames[2]['func'], 'main')


class TestFindDebugErrorFrame(unittest.TestCase):
    """Tests for find_debug_error_frame function."""

    def test_find_debug_error_present(self):
        """find_debug_error_frame returns index of debug_error frame."""
        frames = [
            {'func': 'abort', 'location': 'stdlib/abort.c:73'},
            {'func': 'debug_error', 'location': 'core/source/debug/debug.c:81'},
            {'func': 'm_process__offline', 'location': 'core/source/game_action/offline.c:32'},
        ]
        idx = find_debug_error_frame(frames)
        self.assertEqual(idx, 1)

    def test_find_debug_error_absent(self):
        """find_debug_error_frame returns None when debug_error not present."""
        frames = [
            {'func': 'abort', 'location': 'stdlib/abort.c:73'},
            {'func': 'raise', 'location': 'sysdeps/posix/raise.c:26'},
        ]
        idx = find_debug_error_frame(frames)
        self.assertIsNone(idx)


class TestAdjustFrameForDebugError(unittest.TestCase):
    """Tests for adjust_frame_for_debug_error function."""

    def test_adjust_when_debug_error_found(self):
        """When debug_error is found, frame moves to the caller."""
        frames = [
            {'level': '#0', 'func': 'abort', 'location': 'stdlib/abort.c:73'},
            {'level': '#1', 'func': 'debug_error', 'location': 'core/debug.c:81'},
            {'level': '#2', 'func': 'm_process__offline', 'location': 'offline.c:32'},
        ]
        adjusted, idx, was_adjusted = adjust_frame_for_debug_error(frames)
        self.assertTrue(was_adjusted)
        self.assertEqual(idx, 2)  # Caller of debug_error
        self.assertEqual(adjusted[idx]['func'], 'm_process__offline')

    def test_no_adjust_when_debug_error_absent(self):
        """When debug_error is not found, frame stays at index 0."""
        frames = [
            {'level': '#0', 'func': 'abort', 'location': 'stdlib/abort.c:73'},
            {'level': '#1', 'func': 'raise', 'location': 'raise.c:26'},
        ]
        adjusted, idx, was_adjusted = adjust_frame_for_debug_error(frames)
        self.assertFalse(was_adjusted)
        self.assertEqual(idx, 0)
        self.assertEqual(adjusted[0]['func'], 'abort')

    def test_no_caller_frame(self):
        """When debug_error is last frame, no caller available."""
        frames = [
            {'level': '#0', 'func': 'abort', 'location': 'stdlib/abort.c:73'},
            {'level': '#1', 'func': 'debug_error', 'location': 'debug.c:81'},
        ]
        adjusted, idx, was_adjusted = adjust_frame_for_debug_error(frames)
        self.assertFalse(was_adjusted)
        self.assertEqual(idx, 1)


if __name__ == "__main__":
    unittest.main()
