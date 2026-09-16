"""Scene scanner for the layered architecture.

A self-contained port of the scan pattern from the retired mcp/ and
harness/ shells (harness/debug_scanner_scene.py + mcp/debug_scanner.py +
mcp/gdb_frame_controller.py), built directly on the Layer 1b API
(GDBSession.write) — no dependency on the obsolete mcp/ package.

Wraps ``debug_get_scene_scanner(&game)``, which returns a
DEBUG_Scene_Scanner **by value**; the struct is captured into the gdb
convenience variable ``$debug_scene_scanner`` and its fields are read
with ``-data-evaluate-expression``.

Field layout (core/include/debug/debug_scene.h, guarded by #ifndef
NDEBUG — the symbols are absent in release builds, in which case every
method here degrades to None / {}):

    typedef struct DEBUG_Scene_Scanner_t {
        Scene_Manager *p_scene_manager;
        Scene *p_scene__running;
        Scene *p_scene__current_in__scan;
        m_DEBUG_Scene_Scanner_Func m_refresh;
        m_DEBUG_Scene_Scanner_Func m_iterate_scene;
        m_DEBUG_Scene_Scanner_Func m_go_to__scene;
        Quantity__u32 quantity_of__scenes;
        Scene_Kind the_kind_of__scene;
    } DEBUG_Scene_Scanner;

Key semantics (core/include/defines.h, core/source/scene/scene_manager.c):

    typedef struct Scene_Manager_t {
        Scene scenes[Scene_Kind__Unknown];  // indexed by Scene_Kind
        Scene *p_active_scene;
    } Scene_Manager;

Because the scene array is indexed by Scene_Kind, the kind of any scene
pointer is its element offset from the start of the array — exactly how
the C scanner derives ``the_kind_of__scene``. This module resolves kinds
*inside GDB* (``(Scene_Kind)N``) so the printed enum name is
game-agnostic: it works for any Lavender game whose Scene_Kind enum is
present in the debug info.

Note: the scanner's ``the_kind_of__scene`` post-condition field reflects
the **scan cursor** (p_scene__current_in__scan), *not* the running
scene. Use :meth:`DebugSceneScanner.get_active_scene_kind` for the
active scene's kind.
"""

from __future__ import annotations

import re
from typing import Any

# gdb prints pointers several ways: "0x5555...", "0", "(Scene *) 0x0",
# "0x5555555551c3 <adv_element>" — extract the bare hex token.
_HEX_RE = re.compile(r"(0x[0-9a-fA-F]+|\b\d+\b)")
# Exact null tokens (optionally wrapped in a "(Type)" cast prefix) so a
# real address like 0x1000 (which merely ends in 0) is NOT null.
_NULL_RE = re.compile(r"^\s*(?:\([^()]*\)\s*)?(0x0|0|NULL)\s*$")


def parse_hex(value: str | None) -> str | None:
    """Extract a bare hex/decimal address from a gdb-printed pointer.

    ``parse_hex("0x5555555551c3 <adv_element>")`` → ``"0x5555555551c3"``.
    Returns None for null or unparseable values.
    """
    if value is None:
        return None
    text = value.strip()
    if not text or _NULL_RE.match(text):
        return None
    m = _HEX_RE.search(text)
    return m.group(1) if m else None


def _to_int(value: str | None) -> int | None:
    """Parse a gdb-printed integer (hex or decimal); None if not numeric."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return int(text, 0)
    except ValueError:
        m = re.match(r"^(0x[0-9a-fA-F]+|\d+)", text)
        return int(m.group(1), 0) if m else None


def _is_null(value: str | None) -> bool:
    """True if a gdb-printed value represents a null pointer / 0."""
    if value is None:
        return True
    text = value.strip()
    if not text:
        return True
    return bool(_NULL_RE.match(text))


class DebugSceneScanner:
    """Scene scanner over a GDBSession (Layer 1b API).

    Typical usage (game halted under gdb)::

        scanner = DebugSceneScanner(gdb)
        scanner.get_scanner()            # capture $debug_scene_scanner
        table = scanner.get_table()      # top-level fields
        kind = scanner.get_active_scene_kind()   # the scene that matters
        scenes = scanner.get_scenes_table()      # every allocated scene

    All methods degrade gracefully (None / {}) when the debug symbols
    are unavailable (release build) or the game is not running.
    """

    SCANNER_VAR = "$debug_scene_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_Scene_Scanner_Func"
    _GET_SCANNER_EXPR = "debug_get_scene_scanner(&game)"

    # Field layout of DEBUG_Scene_Scanner (see core/include/debug/debug_scene.h)
    _TOP_LEVEL_FIELDS = (
        "p_scene_manager",
        "p_scene__running",
        "p_scene__current_in__scan",
        "m_refresh",
        "m_iterate_scene",
        "m_go_to__scene",
        "quantity_of__scenes",
        "the_kind_of__scene",
    )

    def __init__(self, gdb) -> None:
        """Args:
            gdb: A GDBSession (mcp_layered.layer_pygdbmi).
        """
        self._gdb = gdb
        self._table_cache: dict | None = None
        self._captured = False

    # -- low-level gdb primitives (Layer 1b) --------------------------------- #

    def _exec(self, stmt: str) -> None:
        """Run an arbitrary gdb console statement (e.g. ``set $x = ...``)."""
        try:
            self._gdb.write(f'-interpreter-exec console "{stmt}"')
        except Exception:
            pass

    def _eval(self, expr: str) -> str | None:
        """Evaluate *expr* via ``-data-evaluate-expression``.

        Returns the printed value (in ``payload["value"]``) or None.
        This is the reliable way to read a value back from gdb.
        """
        try:
            for r in self._gdb.write(f"-data-evaluate-expression {expr}"):
                if r.type.value == "result" and r.raw.get("message") == "done":
                    payload = r.raw.get("payload") or {}
                    return payload.get("value", payload.get("result"))
        except Exception:
            return None
        return None

    def _call(self, expr: str) -> None:
        """Invoke *expr* as a gdb ``call`` (side-effecting; return value
        is only in the console stream, so callers needing values use _eval).
        """
        try:
            self._gdb.write(f'-interpreter-exec console "call {expr}"')
        except Exception:
            pass

    # -- capture ------------------------------------------------------------- #

    def get_scanner(self) -> str | None:
        """Capture the scanner struct by value.

        Executes::

            set $debug_scene_scanner = debug_get_scene_scanner(&game)

        ``&game`` is a global, so no frame switching is needed. Returns
        the captured struct's printed representation, or None on failure
        (e.g. release build without the debug symbols).
        """
        self._table_cache = None
        self._captured = False
        self._exec(f"set {self.SCANNER_VAR} = {self._GET_SCANNER_EXPR}")
        result = self._eval(self.SCANNER_VAR)
        self._captured = result is not None
        return result

    def _ensure_captured(self) -> bool:
        if not self._captured:
            return self.get_scanner() is not None
        return True

    # -- table (single source of truth) -------------------------------------- #

    def get_table(self) -> dict:
        """Return the top-level scanner fields as a dict of gdb strings.

        Reads each field once and caches. Note: ``the_kind_of__scene``
        here is the *scan cursor's* kind, not the active scene's kind
        (see module docstring).
        """
        if self._table_cache is None:
            if not self._ensure_captured():
                self._table_cache = {}
                return self._table_cache
            table: dict[str, Any] = {}
            for field in self._TOP_LEVEL_FIELDS:
                table[field] = self._eval(f"{self.SCANNER_VAR}.{field}")
            self._table_cache = table
        return self._table_cache

    # -- active scene (the fields that matter for scene tracking) ------------- #

    def get_active_scene_kind(self) -> str | None:
        """Kind of the active (running) scene, as a Scene_Kind enum name.

        Scene_Manager.scenes is indexed by Scene_Kind, so the active
        scene's kind is the pointer offset::

            (Scene*)p_scene__running - (Scene*)p_scene_manager->scenes

        resolved to an enum name inside GDB (``(Scene_Kind)N``), which
        makes this game-agnostic. Returns None when the scene manager
        or active scene is null (e.g. before the first transition, or
        in release builds).
        """
        if not self._ensure_captured():
            return None
        mgr = self._eval(f"{self.SCANNER_VAR}.p_scene_manager")
        if _is_null(mgr):
            return None
        active = self._eval(f"{self.SCANNER_VAR}.p_scene__running")
        if _is_null(active):
            return "Scene_Kind__None"
        idx = self._eval(
            f"(Scene*){self.SCANNER_VAR}.p_scene__running"
            f" - (Scene*){self.SCANNER_VAR}.p_scene_manager->scenes"
        )
        idx_int = _to_int(idx)
        if idx_int is None or idx_int < 0:
            return None
        name = self._eval(f"(Scene_Kind){idx_int}")
        if name and not _is_null(name):
            return name.strip()
        return f"Scene_Kind__{idx_int}"

    def get_active_scene_ptr(self) -> str | None:
        """Bare hex address of the active scene (for ptr tracking)."""
        if not self._ensure_captured():
            return None
        active = self._eval(f"{self.SCANNER_VAR}.p_scene__running")
        return parse_hex(active)

    # -- full scene table ------------------------------------------------------ #

    def get_scenes_table(self) -> dict:
        """Map every allocated scene pointer → {"kind": ..., "is_active": ...}.

        Iterates the scanner through the whole scene array (one
        cast-and-call advance per scene; scene counts are small).
        """
        if not self._ensure_captured():
            return {}
        table = self.get_table()
        qty = _to_int(table.get("quantity_of__scenes"))
        if not qty or qty <= 0:
            return {}

        scenes: dict[str, dict] = {}
        for _ in range(qty):
            self._advance("m_iterate_scene")
            ptr_raw = self._eval(f"{self.SCANNER_VAR}.p_scene__current_in__scan")
            kind_raw = self._eval(f"{self.SCANNER_VAR}.the_kind_of__scene")
            ptr = parse_hex(ptr_raw)
            if not ptr:
                continue
            if ptr in scenes:
                break  # wrapped around
            kind = self._normalize_kind(kind_raw)
            is_active = "true" if self._truthy(
                self._eval(f"((Scene *){ptr})->is_active")
            ) else "false"
            scenes[ptr] = {"kind": kind, "is_active": is_active}
        return scenes

    def _normalize_kind(self, value: str | None) -> str:
        """Normalize a gdb-printed Scene_Kind to an enum name string."""
        if value is None:
            return "Scene_Kind__Unknown"
        text = value.strip()
        if not text or _is_null(text):
            return "Scene_Kind__None"
        if text.startswith("Scene_Kind__"):
            return text
        kind_int = _to_int(text)
        if kind_int is None:
            return text
        # No enum names in debug info — numeric placeholder.
        return f"Scene_Kind__{kind_int}"

    @staticmethod
    def _truthy(value: str | None) -> bool:
        if value is None:
            return False
        text = value.strip()
        return text in ("1", "true", "True") or (
            text.isdigit() and int(text) != 0
        )

    # -- advancement (parity with the retired shell's scanner API) ------------ #

    def _advance(self, field: str) -> str | None:
        """Advance the scanner via a function-pointer field (cast-and-call)."""
        self._table_cache = None
        self._exec(
            f"set {self.SCANNER_VAR} = "
            f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.{field})()"
        )
        return self._eval(self.SCANNER_VAR)

    def iterate_scene(self) -> str | None:
        """Advance to the next allocated scene (single call)."""
        return self._advance("m_iterate_scene")

    def go_to__scene(self) -> str | None:
        """Begin transitioning to the scene selected in
        p_scene__current_in__scan (single call)."""
        return self._advance("m_go_to__scene")
