"""clang_tools.py — Pure functions for clangd LSP queries.

Each function takes a ``ClangdSession`` and returns a formatted string
suitable for MCP tool responses.  Future ``scan_*`` domain tools import
these functions directly — they never touch ``clang_server.py``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lavender_tools.lav_ai.clang_server import ClangdSession


def find_definition(session: "ClangdSession", file: str, line: int,
                    column: int) -> str:
    """Find definition of symbol at file:line:column.

    Returns ``"file:line:column"`` string or ``"No definition found."``.
    """
    locations = session.definition(file, line, column)
    if not locations:
        return "No definition found."
    return "\n".join(str(loc) for loc in locations)


def find_references(session: "ClangdSession", file: str, line: int,
                    column: int) -> str:
    """Find all references to symbol at file:line:column.

    Returns newline-separated ``"file:line:column"`` strings
    or ``"No references found."``.
    """
    locations = session.references(file, line, column)
    if not locations:
        return "No references found."
    return "\n".join(str(loc) for loc in locations)


def get_symbols(session: "ClangdSession", file: str) -> str:
    """Get all symbols in a file.

    Returns newline-separated ``"kind name file:line:column"`` strings
    or ``"No symbols found."``.
    """
    symbols = session.document_symbols(file)
    if not symbols:
        return "No symbols found."
    return "\n".join(str(sym) for sym in symbols)


def search_workspace_symbols(session: "ClangdSession", query: str) -> str:
    """Search for symbols matching query across workspace.

    Returns newline-separated ``"kind name file:line:column"`` strings
    or ``"No symbols found."``.
    """
    symbols = session.workspace_symbols(query)
    if not symbols:
        return "No symbols found."
    return "\n".join(str(sym) for sym in symbols)


def get_hover_info(session: "ClangdSession", file: str, line: int,
                   column: int) -> str:
    """Get hover/type info for symbol at file:line:column.

    Returns the hover content string or ``"No hover info available."``.
    """
    result = session.hover(file, line, column)
    if result is None:
        return "No hover info available."
    return result
