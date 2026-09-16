"""Client scanner for the layered architecture.

Wraps the C ``DEBUG_Client_Scanner`` (``core/source/debug/debug_client.c``,
``debug_get_client_scanner(&game)``) over the Layer 1b ``GDBSession.write`` API,
in the same style as :mod:`mcp_layered.debug_scanner_process` /
:mod:`mcp_layered.debug_scanner_scene` (no ``mcp/`` dependency).

The C scanner tracks ONE client at a time (``p_client__current``) plus that
client's inbound / outbound game-action queues, and exposes three advance
functions — each returns the whole struct **by value** and updates the global
``__DEBUG_client_scanner``:

    m_next_client               -> next client slot (wraps modulo the client pool)
    m_next_game_action__inbound -> next allocated inbound game action
    m_next_game_action__outbound-> next allocated outbound game action

Field layout (core/include/debug/debug_client.h, guarded by ``#ifndef NDEBUG`` —
the symbols are absent in release builds, in which case every method here
degrades to None / {} / an error dict):

    typedef struct DEBUG_Client_Scanner_t {
        Game *p_game;
        Client *p_client__current;
        Game_Action *p_game_action__inbound__current;
        Game_Action *p_game_action__outbound__current;
        m_DEBUG_Client_Scanner_Func m_refresh;
        m_DEBUG_Client_Scanner_Func m_next_client;
        m_DEBUG_Client_Scanner_Func m_next_game_action__inbound;
        m_DEBUG_Client_Scanner_Func m_next_game_action__outbound;
        Quantity__u32 quantity_of__clients;
        struct {
            Quantity__u32 quantity_of__game_actions__inbound;
            _Game_Action_Header game_action_header__inbound__current;
            Game_Action_Logic_Entry game_action_logic_entry__inbound__current;
            Quantity__u32 quantity_of__game_actions__outbound;
            _Game_Action_Header game_action_header__outbound__current;
            Game_Action_Logic_Entry game_action_logic_entry__outbound__current;
        } game_actions;
        Identifier__u32 uuid_of__client__current;
        Chunk_Vector__3i32 current_client__local_space__center__3i32;
        Client_Flags__u16 current_client__client_flags__u16;
    } DEBUG_Client_Scanner;

Two capabilities:

1. **Client list** (:meth:`DebugClientScanner.list_clients`) — walk
   ``m_next_client``, collecting each connected client's uuid, flags, and local-space
   center (the ``current_client__local_space__center__3i32`` field is the one that
   reveals a stark center jump, e.g. ``{0, 63, 2}`` while the manager center sits at
   ``{0, 1, 3}``).

2. **Game-action queue snapshot** (:meth:`DebugClientScanner.scan_actions`) — for the
   current client, report the inbound / outbound queue lengths and tally the
   outbound (or inbound) game actions by ``Game_Action_Kind`` by walking
   ``m_next_game_action__<dir>``. This is the diagnostic for a queue **clog**: a
   world-load that mass-drops global spaces parks thousands of
   ``Global_Space__Store`` actions in a client's outbound queue.
"""

from __future__ import annotations

import re
from collections import Counter

from mcp_layered.debug_scanner_scene import _is_null

# GDB annotates a known function pointer as "0xADDR <symbol>".
_FUNC_ANNOT_RE = re.compile(r"<([^>]+)>")

# Deallocated / "unknown" identifier sentinels (defines.h): a client or game
# action whose uuid is one of these is NOT live.
_UUID_SENTINELS = {
    "(identifier__u32)-1", "(identifier__u32)4294967295",
    "-1", "4294967295", "0xffffffff", "0xFFFFFFFF", "unknown",
}


def _normalize_uuid(value: str | None) -> str | None:
    """Normalize a gdb-printed uuid to ``0xXXXXXXXX``.

    Accepts decimal (the common case for these fields, e.g. ``536870912``) or hex;
    the deallocated sentinel (``0xFFFFFFFF`` / ``-1`` / ``unknown``) maps to a token
    in ``_UUID_SENTINELS``; returns None for a genuine 0 (no client / no action).
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if text in _UUID_SENTINELS:
        return "(Identifier__u32)-1"
    try:
        if text.lower().startswith("0x"):
            v = int(text, 16)
        elif "unknown" in text.lower():
            return "(Identifier__u32)-1"
        else:
            v = int(text, 0)
    except ValueError:
        return text
    if v == 0xFFFFFFFF:
        return "(Identifier__u32)-1"
    return f"0x{v:08x}" if v > 0 else None


class DebugClientScanner:
    """Client scanner over a GDBSession (Layer 1b API).

    Typical usage (game HALTED, e.g. at a stuck point)::

        scanner = DebugClientScanner(gdb)
        clients = scanner.list_clients()      # every connected client + center
        queue   = scanner.scan_actions("outbound")  # outbound queue length + kind tally

    All methods degrade gracefully (None / {} / an error dict) when the debug
    symbols are unavailable (release build) or the game is not running.
    """

    SCANNER_VAR = "$debug_client_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_Client_Scanner_Func"
    _GET_SCANNER_EXPR = "debug_get_client_scanner(&game)"
    # Hard cap on client iteration (the real max is config-defined, e.g. 4).
    _MAX_CLIENTS = 64
    # Default cap on game-action iteration for the kind tally (a representative
    # sample; raise via max_iter for a full walk of a large queue).
    _DEFAULT_ACTION_CAP = 512

    def __init__(self, gdb) -> None:
        """Args:
            gdb: A GDBSession (mcp_layered.layer_pygdbmi).
        """
        self._gdb = gdb
        self._captured = False

    # -- low-level gdb primitives (Layer 1b) --------------------------------- #

    def _eval(self, expr: str) -> str | None:
        """Evaluate *expr* via ``-data-evaluate-expression`` (a read, not a call).

        Returns the printed value (in ``payload["value"]``) or None.
        """
        try:
            for r in self._gdb.write(f"-data-evaluate-expression {expr}"):
                if r.type.value == "result" and r.raw.get("message") == "done":
                    payload = r.raw.get("payload") or {}
                    return payload.get("value", payload.get("result"))
        except Exception:
            return None
        return None

    def _exec(self, stmt: str) -> None:
        """Run an arbitrary gdb console statement (e.g. ``set $x = ...``)."""
        try:
            self._gdb.write(f'-interpreter-exec console "{stmt}"')
        except Exception:
            pass

    # -- C-scanner capture + advancement ------------------------------------- #

    def get_scanner(self) -> str | None:
        """Capture the C scanner by value::

            set $debug_client_scanner = debug_get_client_scanner(&game)

        ``&game`` is a global, so no frame switching is needed. The call also
        seeds the scanner at client[0] and the first allocated game action of each
        queue. Returns the captured struct's printed representation, or None on
        failure (release build, or the game/world not started). MUST be called
        while the game is HALTED (the call runs in the inferior).
        """
        self._captured = False
        self._exec(f"set {self.SCANNER_VAR} = {self._GET_SCANNER_EXPR}")
        result = self._eval(self.SCANNER_VAR)
        self._captured = result is not None and not _is_null(result)
        return result

    def _ensure_captured(self) -> bool:
        if not self._captured:
            return self.get_scanner() is not None
        return True

    def _advance(self, field: str) -> str | None:
        """Advance the scanner via a function-pointer field (cast-and-call),
        returning the scanner's printed state after the call.

        gdb cannot call a function pointer stored inside a convenience variable,
        so it is cast to its named type first::

            set $var = ((m_DEBUG_Client_Scanner_Func)$var.<field>)()
        """
        self._exec(
            f"set {self.SCANNER_VAR} = "
            f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.{field})()"
        )
        return self._eval(self.SCANNER_VAR)

    # -- struct parsing ------------------------------------------------------ #

    @staticmethod
    def _extract_block(text: str, key: str) -> str | None:
        """Return the balanced ``{...}`` content following ``key = `` in *text*.

        None when *key* (or its opening brace) is not found. Used to isolate the
        nested ``game_actions`` / ``*_header__current`` / ``_serialiation_header``
        / center blocks from the flat printed struct.
        """
        idx = text.find(key)
        if idx < 0:
            return None
        brace = text.find("{", idx)
        if brace < 0:
            return None
        depth = 0
        for i in range(brace, len(text)):
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return text[brace + 1:i]
        return None

    def _parse_struct(self, struct_text: str | None) -> dict | None:
        """Parse one printed scanner struct into a flat dict.

        Returns None when the struct is null/unparseable. Keys:
        ``uuid`` (current client), ``flags``, ``center`` (``{x,y,z}``),
        ``client_count``, and per-queue ``ga_<dir>_count`` / ``ga_<dir>_kind`` /
        ``ga_<dir>_uuid`` for ``dir`` in (inbound, outbound).
        """
        if not struct_text or _is_null(struct_text):
            return None

        result: dict = {
            "uuid": None,
            "flags": None,
            "center": None,
            "client_count": None,
            "ga_inbound_count": None,
            "ga_outbound_count": None,
            "ga_inbound_kind": None,
            "ga_outbound_kind": None,
            "ga_inbound_uuid": None,
            "ga_outbound_uuid": None,
        }

        m = re.search(r"quantity_of__clients\s*=\s*(\d+)", struct_text)
        if m:
            result["client_count"] = int(m.group(1))

        m = re.search(r"uuid_of__client__current\s*=\s*(\S+?)\s*[,}]", struct_text)
        if m:
            result["uuid"] = _normalize_uuid(m.group(1))

        # u16 flags print as "1 '\001'"; capture the leading digits only (a bare
        # value followed by the struct's closing brace would otherwise bleed in).
        m = re.search(r"current_client__client_flags__u16\s*=\s*(\d+)", struct_text)
        if m:
            result["flags"] = m.group(1)

        center_block = self._extract_block(
            struct_text, "current_client__local_space__center__3i32")
        if center_block:
            center: dict[str, int] = {}
            for axis in ("x", "y", "z"):
                am = re.search(rf"{axis}__i32\s*=\s*(-?\d+)", center_block)
                if am:
                    center[axis] = int(am.group(1))
            if center:
                result["center"] = center

        ga_block = self._extract_block(struct_text, "game_actions")
        if ga_block:
            m = re.search(r"quantity_of__game_actions__inbound\s*=\s*(\d+)", ga_block)
            if m:
                result["ga_inbound_count"] = int(m.group(1))
            m = re.search(r"quantity_of__game_actions__outbound\s*=\s*(\d+)", ga_block)
            if m:
                result["ga_outbound_count"] = int(m.group(1))
            for direction in ("inbound", "outbound"):
                hdr = self._extract_block(
                    ga_block, f"game_action_header__{direction}__current")
                if not hdr:
                    continue
                km = re.search(
                    r"the_kind_of_game_action__this_action_is\s*=\s*(\w+)", hdr)
                result[f"ga_{direction}_kind"] = km.group(1) if km else None
                hdr_inner = self._extract_block(hdr, "_serialiation_header")
                if hdr_inner:
                    # uuid is the LAST field in _serialiation_header, so its
                    # value ends at the block boundary (no trailing comma) —
                    # allow end-of-string as the terminator.
                    um = re.search(r"uuid\s*=\s*(\S+?)(?:\s*[,}]|\s*$)", hdr_inner)
                    if um:
                        result[f"ga_{direction}_uuid"] = _normalize_uuid(um.group(1))
        return result

    @staticmethod
    def _is_live_uuid(uuid) -> bool:
        """True if *uuid* denotes a live (allocated) client / game action."""
        if not uuid or uuid == 0:
            return False
        if isinstance(uuid, str) and (
                uuid == "(Identifier__u32)-1" or uuid in _UUID_SENTINELS):
            return False
        return True

    # -- capabilities -------------------------------------------------------- #

    def list_clients(self, max_iter: int | None = None) -> dict:
        """Walk ``m_next_client`` and collect every connected client.

        Returns ``{"count": N, "declared": <quantity_of__clients>, "clients":
        [{uuid, flags, center}, ...]}``, or an ``{"error": ...}`` dict when the
        scanner is unavailable. Unconnected slots (uuid sentinel) are skipped; the
        walk stops when it wraps back to an already-seen client or after *max_iter*
        (default ``_MAX_CLIENTS``). Must be called while the game is HALTED.
        """
        if not self._ensure_captured():
            return {"error": "client scanner unavailable (release build, or game "
                             "not started / not halted)",
                    "count": 0, "declared": None, "clients": []}
        cap = max_iter if max_iter is not None else self._MAX_CLIENTS
        clients: dict[str, dict] = {}
        order: list[str] = []
        declared = None
        printout = self._eval(self.SCANNER_VAR)
        for _ in range(cap):
            parsed = self._parse_struct(printout)
            if parsed is None:
                break
            if declared is None:
                declared = parsed.get("client_count")
                if declared == 0:
                    break  # no connected clients
            uuid = parsed.get("uuid")
            if self._is_live_uuid(uuid) and uuid not in clients:
                clients[uuid] = {
                    "uuid": uuid,
                    "flags": parsed.get("flags"),
                    "center": parsed.get("center"),
                }
                order.append(uuid)
            elif self._is_live_uuid(uuid):
                break  # wrapped around to an already-seen connected client
            printout = self._advance("m_next_client")
            if printout is None:
                break
        return {"count": len(clients), "declared": declared,
                "clients": [clients[u] for u in order]}

    def scan_actions(self, direction: str = "outbound",
                     max_iter: int | None = None) -> dict:
        """Snapshot the current client's game-action queue.

        Reports the inbound / outbound queue lengths (read directly) and tallies
        the requested queue's actions by ``Game_Action_Kind`` by walking
        ``m_next_game_action__<direction>``, deduping by the action uuid and
        stopping on wrap (or after *max_iter*). The default cap is a representative
        sample (``_DEFAULT_ACTION_CAP``) so a very large queue does not force an
        unbounded GDB walk; pass a larger *max_iter* for a full tally.

        Returns::

            {"direction", "inbound_count", "outbound_count", "total",
             "tallied", "complete", "by_kind": {kind: count},
             "current_kind", "current_uuid"}

        or an ``{"error": ...}`` dict when the scanner is unavailable. Must be
        called while the game is HALTED.
        """
        if direction not in ("inbound", "outbound"):
            return {"error": f"direction must be 'inbound' or 'outbound', "
                             f"got {direction!r}",
                    "direction": direction, "inbound_count": 0, "outbound_count": 0,
                    "total": 0, "tallied": 0, "complete": False, "by_kind": {}}
        if not self._ensure_captured():
            return {"error": "client scanner unavailable (release build, or game "
                             "not started / not halted)",
                    "direction": direction, "inbound_count": 0, "outbound_count": 0,
                    "total": 0, "tallied": 0, "complete": False, "by_kind": {}}

        field = f"m_next_game_action__{direction}"
        printout = self._eval(self.SCANNER_VAR)
        first = self._parse_struct(printout)
        if first is None:
            return {"error": "could not parse client scanner struct",
                    "direction": direction, "inbound_count": 0, "outbound_count": 0,
                    "total": 0, "tallied": 0, "complete": False, "by_kind": {}}

        inbound_count = first.get("ga_inbound_count") or 0
        outbound_count = first.get("ga_outbound_count") or 0
        total = outbound_count if direction == "outbound" else inbound_count
        if max_iter is not None:
            cap = int(max_iter)
        else:
            # Default: a fixed sample (independent of `total`) so the walk has
            # headroom to step over any deallocated slots while still bounding a
            # huge queue. In a healthy queue the wrap detection (below) stops it
            # as soon as every live action has been tallied, so a small queue is
            # never over-walked.
            cap = self._DEFAULT_ACTION_CAP if total else 0

        by_kind: Counter = Counter()
        seen: set = set()
        tallied = 0
        parsed = first
        for _ in range(cap):
            key = parsed.get(f"ga_{direction}_uuid")
            if key in seen:
                break  # wrapped around to a live action we already tallied
            if not self._is_live_uuid(key):
                # Deallocated current — unexpected in a healthy state (the C
                # scanner skips deallocated slots), but it can occur in a
                # crashed/corrupted one. Advance past it instead of bailing, so
                # the live actions that survive are still reached.
                printout = self._advance(field)
                if printout is None:
                    break
                parsed = self._parse_struct(printout)
                if parsed is None:
                    break
                continue
            seen.add(key)
            by_kind[parsed.get(f"ga_{direction}_kind") or "<unknown>"] += 1
            tallied += 1
            printout = self._advance(field)
            if printout is None:
                break
            parsed = self._parse_struct(printout)
            if parsed is None:
                break

        return {
            "direction": direction,
            "inbound_count": inbound_count,
            "outbound_count": outbound_count,
            "total": total,
            "tallied": tallied,
            "complete": (tallied >= total) if total else True,
            "by_kind": dict(by_kind.most_common()),
            "current_kind": first.get(f"ga_{direction}_kind"),
            "current_uuid": first.get(f"ga_{direction}_uuid"),
        }
