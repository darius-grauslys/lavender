"""Tests for mcp.gdb_nav_utils (step_frame_detailed / _poll_for_stops).

Focus: the frame-heartbeat WATCHDOG. With -DCRASH_ON_ERROR dropped, a
non-fatal error can leave the game alive but stuck inside one frame (e.g.
an infinite debug_error retry loop). The bp storm keeps the GDB idle
timeout alive, so only a watchdog keyed to FRAME BOUNDARY crossings
(heartbeat hits) can detect it: the watchdog deadline is extended only on
heartbeat hits, never on bursty hook hits.

Timing is made deterministic with a fake clock: each scripted
get_gdb_response() call advances it by a fixed number of time units, so
no test depends on real wall time.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, _REPO_ROOT)

import mcp.gdb_nav_utils as nav  # noqa: E402


class _FakeClock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def advance(self, dt):
        self.now += dt


def _stopped(func, bpnum):
    return {
        "type": "notify", "message": "stopped",
        "payload": {"reason": "breakpoint-hit", "bkptno": str(bpnum),
                    "frame": {"func": func, "file": "x.c", "line": "1"}},
    }


def _make_controller(records, clock, step=2.0):
    """A GdbController double.

    - write(): -break-insert returns a done record with bp number 7;
      everything else (continue/delete) returns [].
    - get_gdb_response(): pops one scripted record per call (None when
      exhausted) and advances the fake clock by `step` time units.
    """
    gdb = MagicMock()
    # _poll_for_stops probes these via hasattr; give them real behavior.
    gdb._skip_hooks = False
    gdb.process_hooks_on_raw = MagicMock()

    queue = list(records)

    def get_response(*args, **kwargs):
        record = queue.pop(0) if queue else None
        clock.advance(step)
        return record

    gdb.get_gdb_response.side_effect = get_response

    def write(cmd, *args, **kwargs):
        if cmd.startswith("-break-insert"):
            return [{"type": "result", "message": "done",
                     "payload": {"bkpt": {"number": "7"}}}]
        return []

    gdb.write.side_effect = write
    return gdb


class TestStepFrameWatchdog(unittest.TestCase):
    """step_frame_detailed watchdog: extended ONLY on heartbeat (frame
    boundary) hits, never on bursty hook hits."""

    HB = "reset__game_tick_timer"
    TARGET = "manage_game__post_render"

    def _step(self, records, watchdog, heartbeat_func, step=2.0):
        clock = _FakeClock()
        gdb = _make_controller(records, clock, step=step)
        with patch.object(nav.time, "monotonic", clock.monotonic):
            return nav.step_frame_detailed(
                gdb, self.TARGET, timeout=watchdog,
                heartbeat_func=heartbeat_func)

    def test_target_hit(self):
        hit, reason = self._step([_stopped(self.TARGET, 7)], 3.0, self.HB)
        self.assertTrue(hit, f"expected target hit, got {reason!r}")
        self.assertIsNone(reason)

    def test_heartbeat_extends_watchdog(self):
        """Two heartbeat crossings (2 time units apart) inside a 3-unit
        watchdog keep the step alive long enough to reach the target.
        Without extension the deadline (3) would expire after the second
        crossing (clock at 4)."""
        recs = [_stopped(self.HB, 9),
                _stopped(self.HB, 9),
                _stopped(self.TARGET, 7)]
        hit, reason = self._step(recs, 3.0, self.HB)
        self.assertTrue(
            hit, f"heartbeat should extend the watchdog, got {reason!r}")

    def test_bp_storm_does_not_extend_watchdog(self):
        """Repeated NON-heartbeat stops (a stuck game in a non-fatal error
        loop) keep arriving but do NOT extend the watchdog: after 2 stops
        (2 units apart) the clock is past the 3-unit deadline and the step
        reports timeout instead of hanging forever."""
        recs = [_stopped("debug_error", 5) for _ in range(4)]
        hit, reason = self._step(recs, 3.0, self.HB)
        self.assertFalse(hit)
        self.assertEqual(reason, "timeout")

    def test_same_traffic_without_heartbeat_awareness_times_out(self):
        """Contrast: the SAME traffic as test_heartbeat_extends_watchdog,
        but with heartbeat_func=None (legacy behavior) — the stops are just
        'unexpected_bp', the deadline is never extended, and the step
        times out. This is exactly why the heartbeat distinction exists."""
        recs = [_stopped(self.HB, 9),
                _stopped(self.HB, 9),
                _stopped(self.TARGET, 7)]
        hit, reason = self._step(recs, 3.0, None)
        self.assertFalse(hit)
        self.assertEqual(reason, "timeout")

    def test_unbounded_watchdog_ignores_storm(self):
        """timeout=0 (legacy unbounded): the storm never times out and the
        step reaches the target (behavior preserved for opt-out users)."""
        recs = ([_stopped("debug_error", 5) for _ in range(3)]
                + [_stopped(self.TARGET, 7)])
        hit, reason = self._step(recs, 0.0, self.HB)
        self.assertTrue(hit, f"unbounded step should reach target, got {reason!r}")


class TestPollForStopsHeartbeat(unittest.TestCase):
    HB = "reset__game_tick_timer"

    def _poll(self, records, heartbeat_func, deadline=float("inf")):
        clock = _FakeClock()
        gdb = _make_controller(records, clock, step=0.5)
        with patch.object(nav.time, "monotonic", clock.monotonic):
            return nav._poll_for_stops(
                gdb, 7, deadline, 0.0, heartbeat_func=heartbeat_func)

    def test_heartbeat_classified(self):
        hit, detail = self._poll([_stopped(self.HB, 9)], self.HB)
        self.assertFalse(hit)
        self.assertEqual(detail, "heartbeat")

    def test_heartbeat_only_when_requested(self):
        """Without heartbeat_func the same stop is an unexpected_bp."""
        hit, detail = self._poll([_stopped(self.HB, 9)], None)
        self.assertFalse(hit)
        self.assertEqual(detail, "unexpected_bp")

    def test_other_bp_is_unexpected(self):
        hit, detail = self._poll([_stopped("debug_error", 5)], self.HB)
        self.assertFalse(hit)
        self.assertEqual(detail, "unexpected_bp")

    def test_target_hit(self):
        hit, detail = self._poll([_stopped("whatever", 7)], self.HB)
        self.assertTrue(hit)
        self.assertEqual(detail, "whatever")


if __name__ == "__main__":
    unittest.main(verbosity=2)
