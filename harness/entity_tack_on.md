# Field layout of DEBUG_Entity_Scanner (see core/include/debug/debug_entity.h).
# Mirrors the C source so harness names and C side agree.
DEBUG_ENTITY_SCANNER_FIELDS = (
    "p_entity_manager",
    "p_entity__current",
    "m_next_entity",
)


class DebugEntityScannerExplorer(GDBFrameController):
    """
    Inspects entity state through debug_entity.h's ``debug_get_entity_scanner``.

    Typical loop (game halted under gdb):
        explorer = DebugEntityScannerExplorer(gdbmi)
        explorer.get_ui_scanner()                 # captures $debug_entity_scanner
        explorer.read_field("p_entity_manager")
        explorer.read_fields()                    # all DEBUG_Entity_Scanner fields
        explorer.next_entity()                    # advance via m_next_entity

    debug_get_entity_scanner returns a DEBUG_Entity_Scanner by value, so the
    scanner is captured by value into the convenience variable
    ``$debug_entity_scanner`` and fields are read with ``.`` member access.
    """

    SCANNER_VAR = "$debug_entity_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_Entity_Scanner_Func"

    def get_ui_scanner(self) -> str | None:
        """Call ``debug_get_entity_scanner(&game)`` and capture the struct.

        Executes (in the main frame) ``set $debug_entity_scanner =
        debug_get_entity_scanner(&game)`` and returns the captured struct's
        printed representation (or ``None`` on failure).
        """
        self.push_main_frame()
        try:
            self._exec(
                f"set {self.SCANNER_VAR} = debug_get_entity_scanner(&game)"
            )
        finally:
            self.pop_frame()
        return self._eval(self.SCANNER_VAR)

    def read_field(self, field: str) -> str | None:
        """Return the gdb-printed value of ``$debug_entity_scanner.<field>``."""
        if field not in DEBUG_ENTITY_SCANNER_FIELDS:
            raise ValueError(f"unknown DEBUG_Entity_Scanner field: {field!r}")
        return self._eval(f"{self.SCANNER_VAR}.{field}")

    def read_fields(self) -> dict[str, str | None]:
        """Snapshot every DEBUG_Entity_Scanner field into a dict."""
        return {f: self.read_field(f) for f in DEBUG_ENTITY_SCANNER_FIELDS}

    def next_entity(self) -> str | None:
        """Advance the scanner via ``m_next_entity`` and return the new
        struct's printed representation.

        gdb cannot call a function pointer stored inside a convenience
        variable (error: "Attempt to take address of value not located in
        memory"). We work around this by casting-and-calling, exactly like
        DebugUIScannerExplorer.next_element:
            set $debug_entity_scanner =
                ((m_DEBUG_Entity_Scanner_Func)$debug_entity_scanner.m_next_entity)()
        """
        self.push_main_frame()
        try:
            self._exec(
                f"set {self.SCANNER_VAR} = "
                f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.m_next_entity)()"
            )
        finally:
            self.pop_frame()
        return self._eval(self.SCANNER_VAR)
