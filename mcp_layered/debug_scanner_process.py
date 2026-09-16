"""Process scanner for the layered architecture (Layer 1c).

Two capabilities, both over the Layer 1b ``GDBSession.write`` API (no ``mcp/``
dependency):

1. **Handler resolution** (``resolve_handler_name`` / ``scan``) — resolve a
   process's **run-handler name** from its pointer, at a *safe* point (the game
   halted under a scanner context). Property 4 of ``PLANS/process_trace.md``.
   Used by the process create/remove trace to name the handler behind each
   create/remove/error event.

   Why a safe, deferred read (and not at the breakpoint hit): a process's
   ``m_process_run__handler`` is **bound after creation** — the creating callee
   sets it *after* ``add_process_to__process_table`` returns, so at the
   create/remove/error hit the handler is often still NULL. It is a *stable*
   value once bound (unlike the callee stack, which is gone once a transient
   stop is continued past), so it is read later, when the game is halted — both
   **safe** (no transient-stop / nested-read deadlock) and **correct**.

2. **Pool snapshot** (``scan_pool``) — enumerate the *entire* process pool via
   the C ``DEBUG_Process_Scanner`` (``core/source/debug/debug_process.c``,
   ``debug_get_process_scanner(&game)``). The scanner walks the active process
   ring (``process_table.ptr_array_of__processes[PROCESS_MAX_QUANTITY_OF]``,
   skipping null/deallocated) and exposes a full ``copy_of__process__current``.
   We advance it with ``m_iterate_process``, dedupe by the process uuid, and stop
   when the ring cycles back — so we never depend on the scanner's (currently
   unpopulated) ``quantity_of__processes``. The result is a summary of how full
   the pool is and *which handlers* occupy it — the diagnostic that separates a
   pool **saturation** (capacity) problem from a specific handler over-
   accumulating (leak).

Field layout of ``DEBUG_Process_Scanner`` (core/include/debug/debug_process.h,
guarded by ``#ifndef NDEBUG`` — the symbols are absent in release builds, in
which case every method here degrades to None / {}):

    typedef struct DEBUG_Process_Scanner_t {
        Process_Manager         *p_process_manager;
        Process                 *p_process__current;
        Process                **p_ptr_process__current;
        m_DEBUG_Process_Scanner_Func m_refresh;
        m_DEBUG_Process_Scanner_Func m_iterate_process;
        Quantity__u32            quantity_of__processes;   // NOT populated (see above)
        Process                  copy_of__process__current;
    } DEBUG_Process_Scanner;
"""

from __future__ import annotations

import re
from collections import Counter

from mcp_layered.debug_scanner_scene import parse_hex, _is_null

# GDB annotates a known function pointer as "0xADDR <symbol>".
_FUNC_ANNOT_RE = re.compile(r"<([^>]+)>")
# A bare hex address token.
_HEX_RE = re.compile(r"0x[0-9a-fA-F]+")

# Deallocated serialization-header uuid sentinels (defines.h): a slot whose
# _serialization_header.uuid is one of these is NOT an allocated process.
_UUID_SENTINELS = {
    "(identifier__u32)-1", "(identifier__u32)4294967295",
    "-1", "4294967295", "0xffffffff", "0xFFFFFFFF",
}


class DebugProcessScanner:
    """Process scanner over a GDBSession (Layer 1b API).

    Handler resolution (game halted under a scanner context)::

        scanner = DebugProcessScanner(gdb)
        name = scanner.resolve_handler_name("0x5555556e30d0")
        # -> "m_process_run__handler__fs"  (or the raw addr, or None)

    Pool snapshot (game HALTED, e.g. at a stuck point)::

        scanner = DebugProcessScanner(gdb)
        scanner.get_scanner()
        pool = scanner.scan_pool()
        # -> {"capacity": 512, "active": N, "free": 512-N, "saturated": bool,
        #     "by_handler": {...}, "by_kind": {...}, "processes": {...}}

    All methods degrade gracefully (None / {} / an error dict) when the debug
    symbols are unavailable (release build) or the game is not running.
    """

    SCANNER_VAR = "$debug_process_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_Process_Scanner_Func"
    _GET_SCANNER_EXPR = "debug_get_process_scanner(&game)"
    # PROCESS_MAX_QUANTITY_OF (core/include/defines.h) — the pool slot count.
    # The C scanner's active ring is this many entries; a snapshot walks at most
    # this many before the ring must cycle back.
    _POOL_CAPACITY = 512

    def __init__(self, gdb) -> None:
        """Args:
            gdb: A GDBSession (mcp_layered.layer_pygdbmi).
        """
        self._gdb = gdb
        self._captured = False
        self._table_cache: dict | None = None

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

    # -- handler resolution (property 4) ------------------------------------- #

    def resolve_handler_name(self, ptr: str | None,
                             cache: dict | None = None) -> str | None:
        """Resolve the run-handler's function name for a process pointer.

        Reads ``((Process *)<ptr>)->m_process_run__handler`` and resolves the
        function name from GDB's ``<symbol>`` annotation (falling back to a
        ``-data-evaluate-expression (void*)<addr>`` re-read, then the raw addr).
        Returns the handler name, the raw address (if not a known symbol), or
        None (null process / unbound handler). Must be called at a safe point
        (game halted). *cache* (addr->name) dedupes symbol lookups.
        """
        addr = parse_hex(ptr)
        if addr is None or _is_null(addr):
            return None
        if cache is not None:
            key = f"handler:{addr}"
            if key in cache:
                return cache[key]

        val = self._eval(f"((Process *){addr})->m_process_run__handler")
        name: str | None = None
        if val is not None and not _is_null(val):
            handler_addr = None
            m = _HEX_RE.search(val)
            if m:
                handler_addr = m.group(0)
            # 1) The evaluated function pointer usually carries the annotation.
            am = _FUNC_ANNOT_RE.search(val)
            if am:
                name = am.group(1)
            elif handler_addr is not None:
                # 2) Re-read cast to a plain pointer to surface the annotation.
                if cache is not None and handler_addr in cache:
                    name = cache[handler_addr]
                else:
                    ann = self._eval(f"(void*){handler_addr}")
                    a2 = _FUNC_ANNOT_RE.search(ann or "")
                    name = a2.group(1) if a2 else handler_addr
                    if cache is not None:
                        cache[handler_addr] = name
            else:
                name = val.strip()
        if cache is not None:
            cache[f"handler:{addr}"] = name
        return name

    def scan(self, ptr: str | None, cache: dict | None = None) -> dict:
        """Return {"ptr": ..., "handler": ...} for a process pointer."""
        addr = parse_hex(ptr)
        return {"ptr": addr, "handler": self.resolve_handler_name(addr, cache)}

    # -- C-scanner capture + advancement (for the pool snapshot) ------------- #

    def get_scanner(self) -> str | None:
        """Capture the C scanner by value::

            set $debug_process_scanner = debug_get_process_scanner(&game)

        ``&game`` is a global, so no frame switching is needed. Returns the
        captured struct's printed representation, or None on failure (release
        build without the symbols, or the game not started). MUST be called
        while the game is HALTED (the call runs in the inferior).
        """
        self._table_cache = None
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
        so we cast it to its named type first::

            set $var = ((m_DEBUG_Process_Scanner_Func)$var.<field>)()
        """
        self._table_cache = None
        self._exec(
            f"set {self.SCANNER_VAR} = "
            f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.{field})()"
        )
        return self._eval(self.SCANNER_VAR)

    # -- pool snapshot ------------------------------------------------------- #

    @staticmethod
    def _copy_block(struct_text: str) -> str | None:
        """Isolate the inner content of the ``copy_of__process__current = {...}``
        brace block from a printed scanner struct. None if not found."""
        key = "copy_of__process__current"
        idx = struct_text.find(key)
        if idx < 0:
            return None
        brace = struct_text.find("{", idx)
        if brace < 0:
            return None
        depth = 0
        for i in range(brace, len(struct_text)):
            c = struct_text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return struct_text[brace + 1:i]
        return None

    @staticmethod
    def _normalize_uuid(value: str | None) -> str | None:
        """Normalize a gdb-printed uuid to ``0xXXXXXXXX``; the deallocated
        sentinel maps to a token in ``_UUID_SENTINELS``; None if not numeric."""
        if value is None:
            return None
        text = value.strip()
        if not text or text in _UUID_SENTINELS:
            return text or None
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

    def _parse_pool_struct(self, struct_text: str | None) -> dict | None:
        """Parse one captured scanner struct into
        ``{uuid, ptr, handler, kind, status, flags, priority}``.

        Returns None when the struct is null/unparseable or the current process
        is deallocated (uuid sentinel) — i.e. there is no live process here.
        """
        if not struct_text or _is_null(struct_text):
            return None
        block = self._copy_block(struct_text)
        if block is None:
            return None

        m = re.search(r"uuid\s*=\s*(\S+?)\s*[,}]", block)
        uuid = self._normalize_uuid(m.group(1)) if m else None
        if uuid is None or uuid in _UUID_SENTINELS:
            return None  # deallocated slot — the C scanner shouldn't yield these, but guard

        # top-level process pointer (for reference / correlation)
        pm = re.search(r"p_process__current\s*=\s*(\S+?)\s*[,}]}", struct_text)
        ptr = parse_hex(pm.group(1)) if pm else None

        # run-handler: "0xADDR <symbol>" | "0xADDR" | "0x0"
        handler = None
        hm = re.search(r"m_process_run__handler\s*=\s*(.+?)(?:,\s*\w+\s*=|\})", block, re.DOTALL)
        if hm:
            hval = hm.group(1).strip()
            am = _FUNC_ANNOT_RE.search(hval)
            if am:
                handler = am.group(1)
            elif not _is_null(hval):
                hx = _HEX_RE.search(hval)
                handler = hx.group(0) if hx else hval

        def _enum(field: str) -> str | None:
            em = re.search(rf"{field}\s*=\s*(\w+)", block)
            return em.group(1) if em else None

        def _scalar(field: str) -> str | None:
            # u8 fields print as e.g. "1 '\\001'" (value + escaped char); take
            # the first token (the numeric value).
            sm = re.search(field + r"\s*=\s*(\S+)", block)
            return sm.group(1) if sm else None

        return {
            "uuid": uuid,
            "ptr": ptr,
            "handler": handler,
            "kind": _enum("the_kind_of__process_this__process_is"),
            "status": _enum("the_kind_of_status__this_process_has"),
            "flags": _scalar("process_flags__u8"),
            "priority": _scalar("process_priority__u8"),
        }

    def scan_pool(self, max_iter: int | None = None) -> dict:
        """Enumerate the whole process pool via the C ``DEBUG_Process_Scanner``.

        Captures ``debug_get_process_scanner(&game)``, then walks the active
        process ring with ``m_iterate_process``, deduping by process uuid and
        stopping when the ring cycles back to an already-seen process (or after
        *max_iter*, defaulting to the pool capacity). Does NOT rely on the
        scanner's unpopulated ``quantity_of__processes``.

        Returns a summary dict::

            {"capacity": 512, "active": N, "free": 512-N, "saturated": bool,
             "by_handler": {handler: count, ...}, "by_kind": {kind: count, ...},
             "processes": {uuid: {uuid, ptr, handler, kind, status, flags, priority}}}

        or ``{"error": ..., ...}`` when the scanner is unavailable. Must be
        called while the game is HALTED.
        """
        capacity = self._POOL_CAPACITY
        if max_iter is None:
            max_iter = capacity
        if not self._ensure_captured():
            return {"error": "process scanner unavailable (release build, or game "
                             "not started / not halted)",
                    "capacity": capacity, "active": 0, "free": capacity,
                    "saturated": False, "by_handler": {}, "by_kind": {},
                    "processes": {}}

        procs: dict[str, dict] = {}
        printout = self._eval(self.SCANNER_VAR)
        for _ in range(max_iter):
            parsed = self._parse_pool_struct(printout)
            if parsed is None:
                break  # empty / deallocated -> no (more) live processes
            uuid = parsed["uuid"]
            if uuid in procs:
                break  # wrapped around the ring to an already-seen process
            procs[uuid] = parsed
            printout = self._advance("m_iterate_process")
            if printout is None:
                break

        by_handler: Counter = Counter()
        by_kind: Counter = Counter()
        for p in procs.values():
            by_handler[p.get("handler") or "<unbound>"] += 1
            by_kind[p.get("kind") or "<unknown>"] += 1

        active = len(procs)
        return {
            "capacity": capacity,
            "active": active,
            "free": max(0, capacity - active),
            "saturated": active >= capacity,
            "by_handler": dict(by_handler.most_common()),
            "by_kind": dict(by_kind.most_common()),
            "processes": procs,
        }
