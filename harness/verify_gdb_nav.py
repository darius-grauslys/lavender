#!/usr/bin/env python3
"""Unit tests for harness/gdb_nav_utils.py — response coordination fix.

The core bug: ``_continue`` used ``gdb.write("-exec-continue")`` which internally
calls ``get_gdb_response(read_response=True)``, consuming the ``*stopped``
notify record if it arrives within pygdbmi's 0.2s additional-output window.
On sequential ``step_frame`` calls (game loop already running), the breakpoint
is hit almost immediately, so ``*running`` and ``*stopped`` can arrive in the
same response batch — ``write()`` eats both, and ``_poll_for_stops`` times out
because the ``*stopped`` it's waiting for was already consumed.

The fix: ``_continue`` now uses ``read_response=False``, so ``write()`` only
sends the command. All response reading is deferred to ``_poll_for_stops``,
which is the sole consumer and correctly handles ``*running`` (ignored) and
``*stopped`` (returned).

Run:
    python3 -m harness.verify_gdb_nav
    python3 harness/verify_gdb_nav.py
"""
from __future__ import annotations

import os
import sys
import time

# Ensure the repo root is on sys.path so the ``harness`` package is importable
# regardless of the current working directory.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from harness.gdb_nav_utils import (
    step_frame,
    _continue,
    _delete_breakpoint,
    _poll_for_stops,
    _add_temporary_breakpoint,
    _normalize_resp,
    _is_breakpoint_hit_response,
    _get_breakpoint_number,
    _get_breakpoint_location,
)


# --------------------------------------------------------------------------- #
#  Test doubles for pygdbmi GdbController
# --------------------------------------------------------------------------- #

class GdbTimeoutError(Exception):
    """Mirrors pygdbmi.constants.GdbTimeoutError."""


class FakeGdbController:
    """Minimal stub of pygdbmi's GdbController for testing response coordination.

    Key behaviors that mirror the real pygdbmi:

    * ``write(cmd, read_response=True)`` — writes the command, and if
      ``read_response`` is True, reads & returns responses from ``_read_queue``.
      If ``read_response`` is False, returns ``[]`` without reading anything
      (this is the fix — the real pygdbmi behaves this way too).

    * ``get_gdb_response(timeout_sec, raise_error_on_timeout=True)`` — pops
      the next batch of responses from ``_read_queue``. If the queue is empty,
      raises ``GdbTimeoutError`` (just like real pygdbmi).

    * ``_responses`` is a list of "response batches". Each batch is a list of
      MI record dicts. ``get_gdb_response`` pops one batch at a time.

    This design lets tests precisely control which responses arrive in which
    ``get_gdb_response`` call, simulating real-world timing.
    """

    def __init__(self):
        self._responses: list[list[dict]] = []
        self.write_calls: list[tuple[str, dict]] = []  # (cmd, kwargs)
        self.get_response_calls: int = 0

    def write(self, cmd, timeout_sec=1.0, raise_error_on_timeout=True,
              read_response=True):
        """Write to gdb — record the call and optionally read a response."""
        self.write_calls.append((cmd, {"read_response": read_response,
                                       "timeout_sec": timeout_sec}))
        if read_response:
            return self.get_gdb_response(timeout_sec=timeout_sec,
                                          raise_error_on_timeout=raise_error_on_timeout)
        # read_response=False: just send, don't read — like real pygdbmi.
        return []

    def get_gdb_response(self, timeout_sec=1.0, raise_error_on_timeout=True):
        """Pop the next response batch, or raise GdbTimeoutError if empty."""
        self.get_response_calls += 1
        if self._responses:
            return self._responses.pop(0)
        if raise_error_on_timeout:
            raise GdbTimeoutError(f"No response after {timeout_sec}s")
        return []

    def queue(self, responses: list[dict]):
        """Queue a batch of MI records to be returned by the next get_gdb_response."""
        self._responses.append(responses)

    # Allow checking call history by command prefix.
    def write_cmds(self) -> list[str]:
        return [cmd for cmd, _ in self.write_calls]

    def continue_uses_read_response_false(self) -> bool:
        """Verify that -exec-continue was written with read_response=False."""
        for cmd, kwargs in self.write_calls:
            if cmd == "-exec-continue":
                return kwargs.get("read_response") is False
        return False  # never sent a continue

    def delete_uses_read_response_false(self) -> bool:
        """Verify that -break-delete was written with read_response=False."""
        for cmd, kwargs in self.write_calls:
            if cmd.startswith("-break-delete"):
                return kwargs.get("read_response") is False
        return False


def make_running_record() -> dict:
    """Create a *running notify record (gdb accepted continue)."""
    return {
        "type": "notify",
        "message": "running",
        "payload": {"thread-id": "1"},
        "stream": "stdout",
    }


def make_breakpoint_hit_record(bkptno: int = 1, func: str = "manage_game__post_render") -> dict:
    """Create a *stopped notify record for a breakpoint hit."""
    return {
        "type": "notify",
        "message": "stopped",
        "payload": {
            "reason": "breakpoint-hit",
            "bkptno": str(bkptno),
            "frame": {"func": func, "addr": "0x1000"},
            "thread-id": "1",
        },
        "stream": "stdout",
    }


def make_library_loaded_record() -> dict:
    """Create a library-loaded console record (intermediate noise)."""
    return {
        "type": "console",
        "message": "library-loaded",
        "payload": "{\"name\": \"libSDL2.so\"}",
        "stream": "stdout",
    }


def make_break_insert_done(bkptno: int = 1) -> list[dict]:
    """Create the result record for -break-insert -t."""
    return [{
        "type": "result",
        "message": "done",
        "payload": {
            "bkpt": [{
                "number": str(bkptno),
                "type": "temp",
                "disp": "del",
                "func": "manage_game__post_render",
                "addr": "0x1000",
            }]
        },
        "stream": "stdout",
    }]


# --------------------------------------------------------------------------- #
#  Tests: _normalize_resp and helpers
# --------------------------------------------------------------------------- #

def test_normalize_resp():
    assert _normalize_resp(None) == []
    assert _normalize_resp({}) == []
    assert _normalize_resp({"type": "result"}) == [{"type": "result"}]
    assert _normalize_resp([{"type": "result"}, None, "junk"]) == [{"type": "result"}]


def test_breakpoint_hit_detection():
    rec = make_breakpoint_hit_record(1)
    assert _is_breakpoint_hit_response(rec) is True
    assert _get_breakpoint_number(rec) == 1

    # *running is not a breakpoint hit.
    assert _is_breakpoint_hit_response(make_running_record()) is False
    # None / wrong type.
    assert _is_breakpoint_hit_response(None) is False
    assert _is_breakpoint_hit_response({"type": "result"}) is False
    assert _is_breakpoint_hit_response(
        {"type": "notify", "message": "stopped", "payload": {"reason": "signal-stop"}}) is False


def test_get_breakpoint_location():
    """_get_breakpoint_location should work for both *stopped notifies and
    -break-insert result records."""
    # *stopped (breakpoint-hit) notify: func in payload.frame.func.
    stopped_rec = make_breakpoint_hit_record(1, "manage_game__post_render")
    assert _get_breakpoint_location(stopped_rec) == "manage_game__post_render"

    # -break-insert result: func in payload.bkpt[0].func.
    insert_rec = {
        "type": "result",
        "message": "done",
        "payload": {
            "bkpt": [{
                "number": "1",
                "func": "manage_game__post_render",
                "addr": "0x1000",
            }]
        },
    }
    assert _get_breakpoint_location(insert_rec) == "manage_game__post_render"

    # None / empty.
    assert _get_breakpoint_location(None) is None
    assert _get_breakpoint_location({}) is None


# --------------------------------------------------------------------------- #
#  Test: _continue uses read_response=False
# --------------------------------------------------------------------------- #

def test_continue_uses_read_response_false():
    """_continue must NOT read responses — it should use read_response=False."""
    gdb = FakeGdbController()
    _continue(gdb, timeout=5.0)

    assert gdb.continue_uses_read_response_false(), (
        "_continue should send -exec-continue with read_response=False; "
        "otherwise it may consume the *stopped event"
    )
    # No get_gdb_response calls should have been made by _continue.
    assert gdb.get_response_calls == 0, (
        "_continue should not call get_gdb_response at all"
    )


# --------------------------------------------------------------------------- #
#  Test: _delete_breakpoint uses read_response=False
# --------------------------------------------------------------------------- #

def test_delete_breakpoint_uses_read_response_false():
    gdb = FakeGdbController()
    _delete_breakpoint(gdb, 1, timeout=2.0)

    assert gdb.delete_uses_read_response_false(), (
        "_delete_breakpoint should use read_response=False for consistency"
    )
    assert gdb.get_response_calls == 0, (
        "_delete_breakpoint should not call get_gdb_response at all"
    )


# --------------------------------------------------------------------------- #
#  Test: _poll_for_stops ignores *running, returns on *stopped
# --------------------------------------------------------------------------- #

def test_poll_for_stops_ignores_running_then_returns_stopped():
    """_poll_for_stops should skip *running and return when *stopped arrives."""
    gdb = FakeGdbController()
    # First poll: *running (ignored).
    gdb.queue([make_running_record()])
    # Second poll: breakpoint hit.
    gdb.queue([make_breakpoint_hit_record(1, "manage_game__post_render")])

    deadline = time.monotonic() + 10.0
    hit, detail = _poll_for_stops(gdb, target_bpnum=1, deadline=deadline, timeout=1.0)

    assert hit is True
    assert detail == "manage_game__post_render"


def test_poll_for_stops_unexpected_breakpoint():
    """If a different breakpoint fires, return (False, 'unexpected_bp')."""
    gdb = FakeGdbController()
    gdb.queue([make_breakpoint_hit_record(2, "some_other_func")])

    deadline = time.monotonic() + 10.0
    hit, detail = _poll_for_stops(gdb, target_bpnum=1, deadline=deadline, timeout=1.0)

    assert hit is False
    assert detail == "unexpected_bp"


def test_poll_for_stops_timeout():
    """If no response arrives within the deadline, return (False, 'timeout')."""
    gdb = FakeGdbController()
    # No responses queued — get_gdb_response will raise GdbTimeoutError.

    deadline = time.monotonic() + 0.1  # very short deadline
    hit, detail = _poll_for_stops(gdb, target_bpnum=1, deadline=deadline, timeout=0.5)

    assert hit is False
    assert detail == "timeout"


# --------------------------------------------------------------------------- #
#  Test: _poll_for_stops handles batched *running + *stopped (the bug scenario)
# --------------------------------------------------------------------------- #

def test_poll_for_stops_batched_running_and_stopped():
    """Both *running and *stopped in the same get_gdb_response batch.

    This is the core scenario that was broken. Before the fix, _continue's
    write("-exec-continue") would consume this batch (including *stopped),
    leaving _poll_for_stops with nothing to find. With read_response=False,
    _poll_for_stops receives the batch and correctly processes both records.
    """
    gdb = FakeGdbController()
    # Simulate *running and *stopped arriving in the same chunk.
    gdb.queue([
        make_running_record(),
        make_breakpoint_hit_record(1, "manage_game__post_render"),
    ])

    deadline = time.monotonic() + 10.0
    hit, detail = _poll_for_stops(gdb, target_bpnum=1, deadline=deadline, timeout=1.0)

    assert hit is True
    assert detail == "manage_game__post_render"


# --------------------------------------------------------------------------- #
#  Test: step_frame — first call (slow path, *running then *stopped)
# --------------------------------------------------------------------------- #

def test_step_frame_first_call_slow_path():
    """First call: *running arrives immediately, *stopped arrives later.

    This simulates the program starting from main and taking time to reach
    the breakpoint. Before the fix, this worked because write() only got
    *running (stopped hadn't arrived yet), and _poll_for_stops got *stopped.
    """
    gdb = FakeGdbController()

    # -break-insert -t → done result with bkptno 1.
    gdb.queue(make_break_insert_done(1))
    # First poll after continue: *running (program started, still initializing).
    gdb.queue([make_running_record()])
    # Second poll: *stopped (breakpoint hit).
    gdb.queue([make_breakpoint_hit_record(1, "manage_game__post_render")])
    # Note: _delete_breakpoint uses read_response=False, so no response
    # is queued for -break-delete. The command is sent but not read.

    result = step_frame(gdb, "manage_game__post_render", timeout=5.0)

    assert result is True
    # Verify the command sequence.
    cmds = gdb.write_cmds()
    assert "-break-insert -t manage_game__post_render" in cmds
    assert "-exec-continue" in cmds
    assert "-break-delete 1" in cmds


# --------------------------------------------------------------------------- #
#  Test: step_frame — sequential call (fast path, *running + *stopped batched)
# --------------------------------------------------------------------------- #

def test_step_frame_sequential_call_fast_path():
    """Sequential call: *running and *stopped arrive in the same batch.

    This is the bug scenario. The game loop is already running, so the
    breakpoint is hit almost immediately. *running and *stopped can arrive
    in the same get_gdb_response call. Before the fix, _continue's
    write("-exec-continue") consumed both, and _poll_for_stops timed out.
    With the fix, read_response=False means _poll_for_stops gets the batch.
    """
    gdb = FakeGdbController()

    # -break-insert -t → done result.
    gdb.queue(make_break_insert_done(1))
    # *running + *stopped arrive in the same batch (fast path).
    gdb.queue([
        make_running_record(),
        make_breakpoint_hit_record(1, "manage_game__post_render"),
    ])

    result = step_frame(gdb, "manage_game__post_render", timeout=5.0)

    assert result is True
    assert gdb.continue_uses_read_response_false()


# --------------------------------------------------------------------------- #
#  Test: two consecutive step_frame calls both succeed
# --------------------------------------------------------------------------- #

def test_two_consecutive_step_frame_calls():
    """Two sequential step_frame calls on the same controller.

    This is the main regression test. Before the fix, the first call would
    consume the *stopped event, and the second call would time out because
    there was no *stopped left.
    """
    gdb = FakeGdbController()

    # === First step_frame call ===
    # -break-insert -t → done result.
    gdb.queue(make_break_insert_done(1))
    # *running + *stopped in same batch (game loop already running).
    gdb.queue([
        make_running_record(),
        make_breakpoint_hit_record(1, "manage_game__post_render"),
    ])
    # NOTE: _delete_breakpoint uses read_response=False, so it does NOT
    # consume the -break-delete response. In real gdb, the stale response
    # would be absorbed by the next write() with read_response=True.
    # In this fake, we simply don't queue a response for the delete.

    # === Second step_frame call ===
    # -break-insert -t → done result (new bpnum 2).
    gdb.queue(make_break_insert_done(2))
    # *running + *stopped in same batch (still fast).
    gdb.queue([
        make_running_record(),
        make_breakpoint_hit_record(2, "manage_game__post_render"),
    ])
    # NOTE: same as above — no delete response queued.

    # First call.
    result1 = step_frame(gdb, "manage_game__post_render", timeout=5.0)
    assert result1 is True, "First step_frame should succeed"

    # Second call — this is the one that was broken before the fix.
    result2 = step_frame(gdb, "manage_game__post_render", timeout=5.0)
    assert result2 is True, "Second step_frame should succeed (was broken before fix)"

    # Verify all continues used read_response=False.
    continue_count = sum(1 for cmd, kw in gdb.write_calls if cmd == "-exec-continue")
    assert continue_count == 2, f"Expected 2 continues, got {continue_count}"
    assert gdb.continue_uses_read_response_false()


# --------------------------------------------------------------------------- #
#  Test: step_frame with delayed *stopped (slow path, multi-poll)
# --------------------------------------------------------------------------- #

def test_step_frame_slow_path_multi_poll():
    """Program takes several polls before hitting the breakpoint.

    *running arrives, then several timeouts, then *stopped.
    """
    gdb = FakeGdbController()

    gdb.queue(make_break_insert_done(1))
    # *running
    gdb.queue([make_running_record()])
    # *stopped
    gdb.queue([make_breakpoint_hit_record(1, "manage_game__post_render")])

    result = step_frame(gdb, "manage_game__post_render", timeout=5.0)
    assert result is True


# --------------------------------------------------------------------------- #
#  Test: step_frame timeout (program never reaches breakpoint)
# --------------------------------------------------------------------------- #

def test_step_frame_timeout():
    """Program never reaches the breakpoint — should return False."""
    gdb = FakeGdbController()

    gdb.queue(make_break_insert_done(1))
    # *running, then nothing — program hangs.
    gdb.queue([make_running_record()])
    # -break-delete → done (cleanup after timeout).
    # Note: _delete_breakpoint also uses read_response=False, so it won't
    # queue a response. But we queue one for -break-insert to consume.
    # Actually, _delete_breakpoint doesn't read, so no response needed.

    result = step_frame(gdb, "manage_game__post_render", timeout=0.5)
    assert result is False, "Should timeout when breakpoint is never hit"


# --------------------------------------------------------------------------- #
#  Test: step_frame with unexpected breakpoint, then correct one
# --------------------------------------------------------------------------- #

def test_step_frame_unexpected_then_target():
    """An unexpected breakpoint fires first, then the target one.

    step_frame should continue after unexpected_bp and eventually hit the
    target.
    """
    gdb = FakeGdbController()

    gdb.queue(make_break_insert_done(1))
    # First continue: *running + unexpected breakpoint (bp 2).
    gdb.queue([
        make_running_record(),
        make_breakpoint_hit_record(2, "some_other_func"),
    ])
    # Second continue: *running + target breakpoint (bp 1).
    gdb.queue([
        make_running_record(),
        make_breakpoint_hit_record(1, "manage_game__post_render"),
    ])
    # Note: _delete_breakpoint uses read_response=False.

    result = step_frame(gdb, "manage_game__post_render", timeout=5.0)
    assert result is True


# --------------------------------------------------------------------------- #
#  Test: step_frame with console noise (library-loaded)
# --------------------------------------------------------------------------- #

def test_step_frame_with_console_noise():
    """Console records (library-loaded) should be ignored by _poll_for_stops."""
    gdb = FakeGdbController()

    gdb.queue(make_break_insert_done(1))
    gdb.queue([
        make_running_record(),
        make_library_loaded_record(),
        make_breakpoint_hit_record(1, "manage_game__post_render"),
    ])

    result = step_frame(gdb, "manage_game__post_render", timeout=5.0)
    assert result is True


# --------------------------------------------------------------------------- #
#  Test: _add_temporary_breakpoint reads response correctly
# --------------------------------------------------------------------------- #

def test_add_temporary_breakpoint():
    gdb = FakeGdbController()
    gdb.queue(make_break_insert_done(1))

    bpnum = _add_temporary_breakpoint(gdb, "manage_game__post_render", timeout=2.0)

    assert bpnum == 1, f"Expected bpnum 1, got {bpnum}"
    # Verify -break-insert was sent with read_response=True (to get the result).
    for cmd, kwargs in gdb.write_calls:
        if cmd.startswith("-break-insert"):
            assert kwargs.get("read_response") is not False, (
                "-break-insert should read the response to get the breakpoint number"
            )


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #

def main():
    tests = [
        # Helper tests.
        ("test_normalize_resp", test_normalize_resp),
        ("test_breakpoint_hit_detection", test_breakpoint_hit_detection),
        ("test_get_breakpoint_location", test_get_breakpoint_location),
        # _continue uses read_response=False.
        ("test_continue_uses_read_response_false", test_continue_uses_read_response_false),
        # _delete_breakpoint uses read_response=False.
        ("test_delete_breakpoint_uses_read_response_false",
         test_delete_breakpoint_uses_read_response_false),
        # _poll_for_stops tests.
        ("test_poll_for_stops_ignores_running_then_returns_stopped",
         test_poll_for_stops_ignores_running_then_returns_stopped),
        ("test_poll_for_stops_unexpected_breakpoint",
         test_poll_for_stops_unexpected_breakpoint),
        ("test_poll_for_stops_timeout", test_poll_for_stops_timeout),
        ("test_poll_for_stops_batched_running_and_stopped",
         test_poll_for_stops_batched_running_and_stopped),
        # step_frame tests.
        ("test_step_frame_first_call_slow_path", test_step_frame_first_call_slow_path),
        ("test_step_frame_sequential_call_fast_path",
         test_step_frame_sequential_call_fast_path),
        ("test_two_consecutive_step_frame_calls", test_two_consecutive_step_frame_calls),
        ("test_step_frame_slow_path_multi_poll", test_step_frame_slow_path_multi_poll),
        ("test_step_frame_timeout", test_step_frame_timeout),
        ("test_step_frame_unexpected_then_target", test_step_frame_unexpected_then_target),
        ("test_step_frame_with_console_noise", test_step_frame_with_console_noise),
        # _add_temporary_breakpoint.
        ("test_add_temporary_breakpoint", test_add_temporary_breakpoint),
    ]

    passed = 0
    failed = 0
    for name, func in tests:
        try:
            func()
            print(f"  {name}: OK")
            passed += 1
        except Exception as e:
            print(f"  {name}: FAIL — {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    if failed:
        print("FAILED!")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
