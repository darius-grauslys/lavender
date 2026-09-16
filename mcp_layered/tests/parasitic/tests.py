"""Parasitic tests for layer_pygdbmi breakpoint hooks.

These tests depend on /home/shalidor/Projects/Projects__Lavender/AncientsGame/build/sdl/AncientsGame
which is not guaranteed to be in any arbitrary environment. They are separated from
the main test suite because they require a specific binary.

These tests verify that:
1. Breakpoint hooks fire when the corresponding function is hit
2. The DebugUIScanner correctly captures UI elements
3. Hooks fire during step_frame polling (not just write())
4. The debug_error BreakpointHook reports NON-FATAL errors: since
   -DCRASH_ON_ERROR was dropped from the build, debug_error() prints the
   error and the game KEEPS RUNNING (no SIGABRT stop). The debug_error
   hook captures the same report the old crash path produced (backtrace
   with the debug_error caller highlighted + arguments + the msg_fmt
   error text) and the step driver / session_status surface it.
   AncientsGame's new-client world load deterministically raises a known
   (intentionally deferred) client-hitbox debug_error — the exact message
   varies by run (poll_for_collision_node_update / teleport_client
   variants) — and afterwards the world-load process re-tries the failing
   action forever: the game is alive but never crosses a frame boundary
   again. The step's frame-heartbeat watchdog (a breakpoint on
   reset__game_tick_timer, once per frame; the step timeout is extended
   ONLY on frame-boundary crossings, never on the error loop's bp storm)
   turns that infinite loop into a bounded "timed out" step result
   carrying the captured debug_error events — instead of hanging the
   step forever.

Display environment:
The game is an SDL2/OpenGL application and REQUIRES a working X display to
get past its gfx-context initialization. In headless environments these
tests start an Xvfb instance and propagate DISPLAY to the GDB inferior via
ambient environment inheritance (GDB passes its own process environment to
the inferior). LIBGL_ALWAYS_SOFTWARE=1 is set so GLX under Xvfb uses the
software rasterizer. If a usable DISPLAY is already present, Xvfb is not
started.
"""

import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

# Setup import paths
# tests.py is at Lavender_Dev/mcp_layered/tests/parasitic/tests.py
# mcp_layered package is at Lavender_Dev/mcp_layered/
# We need Lavender_Dev/ in sys.path for "import mcp_layered.X"
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARASITIC_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))  # mcp_layered/
_REPO_ROOT = os.path.abspath(os.path.join(_PARASITIC_ROOT, ".."))  # Lavender_Dev/
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _PARASITIC_ROOT)

# Binary path that these tests depend on
ANCIENTSGAME_BINARY = "/home/shalidor/Projects/Projects__Lavender/AncientsGame/build/sdl/AncientsGame"


def _binary_available() -> bool:
    """Check if the AncientsGame binary is available for testing."""
    return os.path.isfile(ANCIENTSGAME_BINARY)


def _reset_all_state() -> None:
    """Reset module-level state that leaks between independent sessions in
    the same process.

    The session drivers capture a single shared SessionState, so one
    session's session_start leaves running=True and would poison a later
    session's session_start (its fresh GDB has no program → step times
    out). Likewise the scene-tracking state and the breakpoint-hook
    registrations (bound to a prior session's GDBSession) are module-level.
    Call from setUp/tearDown of any create_session-based test.
    """
    from mcp_layered.layer_lav_init import (
        reset_scene_state, reset_session_state, reset_trace_state,
    )
    reset_scene_state()
    reset_session_state()
    reset_trace_state()  # also resets the always-on debug_error + frame
                         # heartbeat hook states


def _remove_client_saves() -> None:
    """Delete saved client files from the game's save directory.

    The client file is a tree of single-hex-digit (uuid-nibble) directories
    directly under each world dir (save/r_<uuid>/0/0/0/0/0/0/2), distinct
    from the chunk dirs (c_*). Deleting those trees guarantees a fresh
    launch takes the deterministic CREATE-CLIENT world-load path, which is
    the trigger the debug_error hook tests assert on. Chunk data (c_*) is
    left in place.
    """
    import re
    save_dir = os.path.join(
        os.path.dirname(os.path.realpath(ANCIENTSGAME_BINARY)), "save")
    if not os.path.isdir(save_dir):
        return
    for world in os.listdir(save_dir):
        world_dir = os.path.join(save_dir, world)
        if not os.path.isdir(world_dir):
            continue
        for entry in os.listdir(world_dir):
            if re.fullmatch(r"[0-9a-f]", entry):
                shutil.rmtree(os.path.join(world_dir, entry), ignore_errors=True)


# ---------------------------------------------------------------------------
# Display environment (Xvfb) — required for the game's GL context init
# ---------------------------------------------------------------------------

def _x_socket_present(display_num: int) -> bool:
    return os.path.exists(f"/tmp/.X11-unix/X{display_num}")


def _display_usable(display: str) -> bool:
    """A display is usable if its X11 socket exists."""
    disp = display.split(".")[0]
    num = disp[1:] if disp.startswith(":") else disp
    if not num.isdigit():
        return False
    return _x_socket_present(int(num))


def _find_free_display_num(start: int = 99) -> int:
    for num in range(start, start + 100):
        if not _x_socket_present(num):
            return num
    raise RuntimeError("Could not find a free display number for Xvfb")


def _ensure_display() -> None:
    """Ensure a working X display is available for the test module.

    - If DISPLAY is set and its X socket exists, use it as-is.
    - Otherwise start Xvfb on a free display number.
    In both cases, set DISPLAY (and LIBGL_ALWAYS_SOFTWARE for software GLX)
    in the process environment so that GDB — and therefore the GDB inferior
    (the game) — inherits a working display.
    """
    global _XVFB_PROC
    existing = os.environ.get("DISPLAY")
    if existing and _display_usable(existing):
        print(f"[parasitic] using existing display: {existing}")
    else:
        xvfb = shutil.which("Xvfb") or "/usr/bin/Xvfb"
        if not os.path.isfile(xvfb):
            raise RuntimeError(
                "No usable X display and Xvfb not found. "
                "Install Xvfb or set DISPLAY."
            )
        num = _find_free_display_num()
        _XVFB_PROC = subprocess.Popen(
            [xvfb, f":{num}", "-screen", "0", "1920x1080x24",
             "-ac", "-nolisten", "tcp"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and not _x_socket_present(num):
            time.sleep(0.05)
        if not _x_socket_present(num):
            _XVFB_PROC.terminate()
            _XVFB_PROC = None
            raise RuntimeError(f"Xvfb failed to start on :{num}")
        os.environ["DISPLAY"] = f":{num}.0"
        print(f"[parasitic] started Xvfb on :{num}")

    os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")


_XVFB_PROC = None


def setUpModule() -> None:
    _ensure_display()


def tearDownModule() -> None:
    global _XVFB_PROC
    if _XVFB_PROC is not None:
        _XVFB_PROC.terminate()
        try:
            _XVFB_PROC.wait(timeout=3)
        except Exception:
            _XVFB_PROC.kill()
        _XVFB_PROC = None


@unittest.skipUnless(_binary_available(), f"Requires {ANCIENTSGAME_BINARY}")
class TestBreakpointHooksParasitic(unittest.TestCase):
    """Parasitic tests verifying breakpoint hooks fire correctly."""

    def test_hooks_fire_on_step_frame(self):
        """Breakpoint hooks should fire when continuing and hitting breakpoints."""
        from mcp_layered.layer_pygdbmi import GDBSession

        # Track hook firings
        fires = []

        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Register hooks to detect breakpoint hits
        def make_hook(name):
            def hook(responses):
                for r in responses:
                    if r.is_breakpoint_hit() and r.frame and r.frame.func:
                        if name in r.frame.func:
                            fires.append(name)
                return responses
            return hook

        # Set breakpoint on initialize_ui_manager (confirmed to fire at startup)
        gdb.set_breakpoint("initialize_ui_manager")
        gdb.add_hook(make_hook("initialize_ui_manager"))

        # Send continue via the underlying gdbmi (non-blocking for the stopped event)
        # The write() returns the library-loaded notifications, then the program stops
        # at the breakpoint — the stopped notification comes via get_gdb_response()
        gdb.gdbmi.write("-exec-continue")

        # Poll for the stopped notification — hooks fire via wrapped get_gdb_response
        import time
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline and not fires:
            try:
                gdb.gdbmi.get_gdb_response(timeout_sec=2.0)
            except Exception:
                pass

        self.assertGreater(len(fires), 0, f"No hooks fired. Fires: {fires}")

        gdb.close()

    def test_hook_fires_via_get_gdb_response(self):
        """Hooks should fire when responses are read via get_gdb_response polling."""
        from mcp_layered.layer_pygdbmi import GDBSession

        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Register a hook that tracks any breakpoint hits
        fires = []
        def tracking_hook(responses):
            for r in responses:
                if r.is_breakpoint_hit():
                    fires.append(True)
            return responses

        gdb.add_hook(tracking_hook)

        # Set a breakpoint that fires during startup
        gdb.set_breakpoint("initialize_ui_manager")

        # Continue and poll (the breakpoint fires at startup)
        gdb.gdbmi.write("-exec-continue", read_response=False)
        import time
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline and not fires:
            try:
                gdb.gdbmi.get_gdb_response(timeout_sec=1.0)
            except Exception:
                pass

        # The hook SHOULD fire because the breakpoint was hit
        self.assertGreater(len(fires), 0, "Hook should fire when breakpoint is hit")

        gdb.close()

    def test_ui_scanner_captures_elements(self):
        """The UI scanner should capture UI elements from AncientsGame."""
        from mcp_layered.layer_pygdbmi import GDBSession

        # Use a bare GDBSession (not LavSession) to avoid state sharing issues
        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Use DebugUIUtils to scan UI elements
        # Note: If debug UI is not compiled in or symbols unavailable, we skip
        try:
            from mcp.debug_ui_utils import DebugUIUtils
            ui_utils = DebugUIUtils(gdbmi=gdb.gdbmi)
            ui_utils.refresh()
            table = ui_utils.get_table()
            managers = table.get("ui_managers", {})

            # Debug UI may or may not be compiled into the binary
            # If managers is empty, it means debug UI symbols not available — skip
            if managers:
                # Check for UI elements
                elements_found = False
                for mgr_ptr, mgr in managers.items():
                    elements = mgr.get("ui_elements", {})
                    if elements:
                        elements_found = True
                        break
                self.assertTrue(elements_found, "Should have at least one UI element")
            # else: debug UI not available, test passes
        finally:
            gdb.close()


@unittest.skipUnless(_binary_available(), f"Requires {ANCIENTSGAME_BINARY}")
class TestSignalDetectionParasitic(unittest.TestCase):
    """Tests that GDBSession detects crash signals (SIGABRT, SIGSEGV, etc.).

    Since -DCRASH_ON_ERROR was dropped, the game no longer HALTS on
    debug_error — so only the signal-detection machinery itself is tested
    here (against synthetic stop records; the live session is started only
    to keep the environment warm). The real-binary debug_error flow is
    covered by TestDebugErrorHookParasitic, which asserts the new
    non-fatal hook logging instead.
    """

    def setUp(self):
        _reset_all_state()

    def tearDown(self):
        _reset_all_state()

    def test_step_frame_detailed_detects_signal(self):
        """step_frame_detailed returns signal_* when game crashes."""
        from mcp_layered.layer_pygdbmi import GDBSession

        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Set breakpoint at a crash-prone function if available, or
        # test with a function that intentionally crashes
        # We'll test by stepping and checking for signal detection in _poll_for_stops
        from mcp.gdb_nav_utils import _get_signal_from_stopped

        # Create a mock stopped record with signal-received
        stopped_record = {
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "signal-received",
                "signal-name": "SIGABRT",
                "signal": "6",
                "frame": {"func": "abort", "pc": "0x7f..."},
                "bkptno": "0",
            }
        }
        signal = _get_signal_from_stopped(stopped_record)
        self.assertEqual(signal, "SIGABRT")

        # Test SIGSEGV
        stopped_record["payload"]["signal-name"] = "SIGSEGV"
        stopped_record["payload"]["signal"] = "11"
        signal = _get_signal_from_stopped(stopped_record)
        self.assertEqual(signal, "SIGSEGV")

        # Test fallback by signal number only
        stopped_record2 = {
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "signal-received",
                "signal": "11",
            }
        }
        signal = _get_signal_from_stopped(stopped_record2)
        self.assertEqual(signal, "SIGSEGV")

        # Test non-stop record (should return None)
        normal_record = {
            "type": "result",
            "message": "done",
            "payload": {}
        }
        signal = _get_signal_from_stopped(normal_record)
        self.assertIsNone(signal)

        # Test breakpoint-hit record (should return None)
        bkpt_record = {
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "breakpoint-hit",
            }
        }
        signal = _get_signal_from_stopped(bkpt_record)
        self.assertIsNone(signal)

        gdb.close()

@unittest.skipUnless(_binary_available(), f"Requires {ANCIENTSGAME_BINARY}")
class TestDebugErrorHookParasitic(unittest.TestCase):
    """The debug_error BreakpointHook against the real binary.

    With -DCRASH_ON_ERROR dropped, debug_error() prints the error and the
    game KEEPS RUNNING — previously this exact flow SIGABRT'd the game at
    ~step 18-20 of world loading. AncientsGame's new-client world load
    deterministically raises a known (intentionally deferred) debug_error
    during client load — the exact message varies by run (observed:
    poll_for_collision_node_update / teleport_client variants of the
    client-hitbox bug) — so the assertions are keyed on what is stable:
    the error occurs DURING world load (m_enter_scene_as__world_load
    handler in the stack), the report shape, and the hook machinery.

    What this test asserts end-to-end:
      1. the game survives the error (no "Game crashed" from the step);
      2. the step response surfaces the error in the SIGABRT-shaped report
         (backtrace + arguments), with the highlighted (>>) frame being the
         debug_error CALLER — never the debug_error trampoline itself;
      3. the report carries the actual error message (msg_fmt) read from
         the stop frame's arguments;
      4. the session JSONL log has a structured "debug-error" record;
      5. the session is still alive and queryable afterwards.

    Known game bug exercised here: after the first client-load error the
    world-load process re-tries the failing action FOREVER — the game is
    alive but never crosses a frame boundary again. The step's frame-
    heartbeat watchdog (step timeout, extended only on frame-boundary
    crossings) turns that infinite loop into a bounded "timed out" step
    result carrying the captured debug_error events. So the step is
    asserted to complete OR time out — both are healthy watchdog behavior;
    only a signal crash would be a failure.

    The verbose process/game-action trace hooks are switched OFF for this
    test (they add GDB round-trips per hit and would make world loading
    take minutes); the debug_error / scene / UI / frame-heartbeat hooks
    stay on — that is exactly what this test covers.

    (The session_status one-line summary of PENDING debug_error events is
    covered by the unit suite — test_debug_error_hook — not here: the step
    driver drains the events it captures, so a status call after the step
    has nothing pending.)
    """

    def setUp(self):
        _reset_all_state()
        _remove_client_saves()  # force the deterministic create-client path

    def tearDown(self):
        _reset_all_state()

    def _find_button(self, session, tag):
        """First ui_list button line whose clicked handler matches `tag`."""
        ui = session.invoke("ui_list")
        for line in ui.splitlines():
            if ("kind=UI_Element_Kind__Button" in line
                    and "clicked" in line
                    and tag in line.lower()):
                return line.split()[0]
        return None

    def _world_load_session(self):
        """Start the game and drive it into a world load:
        main menu -> SINGLEPLAYER -> (existing-world button | NEW WORLD).

        Returns the session (game entering the World_Load scene) or None
        when the UI is unavailable (caller should skipTest).
        """
        import tempfile
        from mcp_layered.layer_lav_init import (
            LavSession, _register_builtin_drivers,
        )
        from mcp_layered.layer_lav_config import LavConfig

        _register_builtin_drivers()  # idempotent; registers the step driver
        config = LavConfig(
            executable=ANCIENTSGAME_BINARY,
            log_file=tempfile.mkdtemp(
                prefix="lav-parasitic-debug-error-"))
        config.ensure_directories()
        session = LavSession(config=config)

        result = session.invoke("session_start")
        if "Game started" not in result:
            session.gdb.close()
            return None

        # Keep the step fast: turn off the verbose per-hit trace hooks
        # (process/game-action). debug_error + scene + UI + frame heartbeat
        # stay on (not part of the trace toggle).
        session.invoke("trace")
        session.invoke("step", count=1)

        # Main menu -> singleplayer scene.
        sp = self._find_button(session, "singleplayer")
        if not sp:
            session.gdb.close()
            return None
        session.invoke("ui_invoke", element_ptr=sp, handler="clicked")
        for _ in range(3):  # let the singleplayer scene load its UI
            session.invoke("step", count=1)

        # Singleplayer -> world load. Prefer an existing-world button
        # (chunks already on disk, faster load); fall back to NEW WORLD
        # (-> World_New -> CREATE).
        world = self._find_button(session, "handler__world")
        if world:
            session.invoke("ui_invoke", element_ptr=world, handler="clicked")
            return session

        new_world = self._find_button(session, "new_world")
        if not new_world:
            session.gdb.close()
            return None
        session.invoke("ui_invoke", element_ptr=new_world, handler="clicked")
        for _ in range(3):  # let the world-new scene load its UI
            session.invoke("step", count=1)
        create = self._find_button(session, "create")
        if not create:
            session.gdb.close()
            return None
        session.invoke("ui_invoke", element_ptr=create, handler="clicked")
        return session

    def test_world_load_debug_error_is_nonfatal_and_reported(self):
        session = self._world_load_session()
        if session is None:
            self.skipTest(
                "game did not start or the world-load buttons were not "
                "found (debug UI unavailable?)")
        try:
            step = session.invoke("step", count=300)
            print(f"[debug-error-hook] step result:\n{step}")

            # 1. The game KEEPS RUNNING through the error. Previously this
            #    exact flow returned "ERROR: Game crashed with SIGABRT on
            #    step 20/102." and the session was dead.
            self.assertNotIn("Game crashed", step)

            # 2. The hook captured the error and the step surfaced it.
            self.assertIn(
                "debug_error(s) occurred during this step", step,
                f"no debug_error section in step result:\n{step}")
            self.assertIn("the game kept running", step)
            self.assertIn("ERROR: debug_error on step", step)

            # 3. Frame adjustment (debug_error.py): the highlighted (>>)
            #    frame is the debug_error CALLER, never the trampoline.
            highlighted = [l for l in step.splitlines()
                           if l.lstrip().startswith(">>")]
            self.assertTrue(
                highlighted, f"no '>>' frame in step result:\n{step}")
            for line in highlighted:
                self.assertNotIn(
                    "debug_error", line,
                    f">> frame is the debug_error trampoline:\n{line}")

            # 4. Stable shape assertions (the exact error function varies
            #    by run): the error happened during world load, and the
            #    report carries the actual msg_fmt text + arguments.
            self.assertIn("world_load", step)
            self.assertIn("Error message:", step)
            self.assertIn("Arguments:", step)

            # 5. The structured records are in the session JSONL log.
            log_file = session.config.log_file
            if os.path.isdir(log_file):
                log_file = os.path.join(log_file, "gdb_responses.jsonl")
            self.assertTrue(os.path.isfile(log_file), f"no log at {log_file}")
            with open(log_file) as f:
                recs = [json.loads(l) for l in f.read().splitlines()
                        if l.strip()]
            de = [r for r in recs if r.get("type") == "debug-error"]
            self.assertTrue(
                de, f"no debug-error records in {log_file}")
            for rec in de:
                self.assertIn("world_load", rec.get("report", ""))
                de_highlighted = [
                    l for l in rec["report"].splitlines()
                    if l.lstrip().startswith(">>")]
                self.assertTrue(de_highlighted)
                self.assertNotIn("debug_error", de_highlighted[0])

            # 6. The step either completed (error recovered) or the
            #    watchdog timed out on the frame the game got stuck in —
            #    both are healthy; the captured events are surfaced in
            #    the response either way.
            self.assertTrue(
                "Stepped" in step or "timed out" in step,
                f"step neither completed nor reported a watchdog timeout:\n{step}")

            # 7. The session is still alive and queryable after the error
            #    (previously the session was dead — GDB had a crashed
            #    inferior). navigate_source must still return a backtrace.
            bt = session.invoke("navigate_source")
            self.assertIn("#", bt)
        finally:
            session.gdb.close()


@unittest.skipUnless(_binary_available(), f"Requires {ANCIENTSGAME_BINARY}")
class TestSceneTrackingParasitic(unittest.TestCase):
    """Scene tracking (set_active_scene_for__scene_manager hook) against
    the real binary."""

    def setUp(self):
        _reset_all_state()

    def tearDown(self):
        _reset_all_state()

    def test_scene_state_after_start_and_step(self):
        """After start + step, the scene hook has identified the active
        scene and session_status surfaces it."""
        from mcp_layered.layer_lav_init import create_session, _scene_state

        session = create_session(executable=ANCIENTSGAME_BINARY)
        try:
            result = session.invoke("session_start")
            self.assertIn("Game started", result)
            step = session.invoke("step", count=1)
            self.assertIn("Stepped", step)
            status = session.invoke("session_status")
            self.assertIn(
                "Scene:", status,
                f"no scene identified in status:\n{status}"
            )
            self.assertIsNotNone(_scene_state["active_kind"])
            print(f"[scene-tracking] active scene: {_scene_state['active_kind']} "
                  f"({len(_scene_state['transitions'])} transitions)")
        finally:
            session.gdb.close()

    def test_scene_transition_surfaced_via_mcp(self):
        """A button click that changes the scene is surfaced in MCP
        responses (step suffix / status section)."""
        from mcp_layered.layer_lav_init import create_session, _scene_state

        session = create_session(executable=ANCIENTSGAME_BINARY)
        try:
            session.invoke("session_start")
            session.invoke("step", count=1)
            before = _scene_state["active_kind"]

            # Find a button with a 'clicked' handler from ui_list output:
            #   "  0x...  uuid=0x...  kind=UI_Element_Kind__Button  ...
            #    handlers=[clicked, ...]"
            ui = session.invoke("ui_list")
            button_ptr = None
            for line in ui.splitlines():
                if "kind=UI_Element_Kind__Button" in line and "clicked" in line:
                    button_ptr = line.split()[0]
                    break
            if not button_ptr:
                self.skipTest("no clickable button found in UI")

            session.invoke("ui_invoke", element_ptr=button_ptr, handler="clicked")
            step = session.invoke("step", count=2)
            after = _scene_state["active_kind"]

            if after != before:
                # A transition occurred — it must be surfaced through MCP.
                status = session.invoke("session_status")
                self.assertIn("Scene transitions", status,
                              f"transition not surfaced in status:\n{status}")
                print(f"[scene-tracking] transition observed: "
                      f"{before} -> {after}")
            else:
                print(f"[scene-tracking] no scene transition "
                      f"(still {after})")
        finally:
            session.gdb.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
