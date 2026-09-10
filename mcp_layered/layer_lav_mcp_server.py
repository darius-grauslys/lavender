"""Layer 6: Session routing and session management middleware.

This layer is responsible for:
- Per-connection session tracking
- Session ID routing
- Forwarding config initialization to Layer 4 on session creation
- Managing the lifecycle of LavSession instances

It wraps the Layer 5 adapter in a session-aware envelope.
"""

from __future__ import annotations

import os
import sys
import threading
import uuid
from typing import Any, Callable

from mcp_layered.layer_lav_init import LavSession, create_session, default_session
from mcp_layered.layer_lav_mcp import MCPAdapter, TOOL_DEFINITIONS


class SessionRegistry:
    """Manages LavSession instances with unique session IDs.

    Thread-safe. Used by Layer 6 to track sessions per MCP connection.
    """

    def __init__(self):
        self._sessions: dict[str, LavSession] = {}
        self._lock = threading.Lock()

    def create(self, session: LavSession | None = None, **session_kwargs) -> str:
        """Create a new session and return its ID.

        Args:
            session: An existing LavSession to register. If None, a new one
                     is created via create_session(**session_kwargs).
            **session_kwargs: Forwarded to create_session() if session is None.

        Returns:
            The unique session ID string.
        """
        if session is None:
            session = create_session(**session_kwargs)

        session_id = uuid.uuid4().hex
        with self._lock:
            self._sessions[session_id] = session
        return session_id

    def get(self, session_id: str) -> LavSession | None:
        """Get a session by ID, or None if not found."""
        with self._lock:
            return self._sessions.get(session_id)

    def get_or_create(self, session_id: str | None = None) -> tuple[str, LavSession]:
        """Get an existing session or create a new one.

        Returns:
            Tuple of (session_id, LavSession).
        """
        if session_id and session_id in self._sessions:
            with self._lock:
                return session_id, self._sessions[session_id]
        new_id = self.create()
        return new_id, self.get(new_id)

    def remove(self, session_id: str) -> bool:
        """Remove a session by ID. Returns True if it existed."""
        with self._lock:
            if session_id in self._sessions:
                session = self._sessions.pop(session_id)
                session.close()
                return True
        return False

    def list_ids(self) -> list[str]:
        """Return a list of all session IDs."""
        with self._lock:
            return list(self._sessions.keys())

    def clear(self) -> int:
        """Close and remove all sessions. Returns the number removed."""
        with self._lock:
            count = len(self._sessions)
            for session in self._sessions.values():
                session.close()
            self._sessions.clear()
        return count

    @property
    def count(self) -> int:
        """Number of active sessions."""
        with self._lock:
            return len(self._sessions)


class SessionManager:
    """Manages the relationship between MCP connections and sessions.

    This is the main entry point for Layer 6. It:
    1. Uses a SessionRegistry to track sessions.
    2. Creates MCPAdapter instances per session.
    3. Routes MCP tool calls to the correct session's adapter.
    """

    def __init__(
        self,
        use_single_session: bool = False,
        default_config_path: str | None = None,
        default_executable: str | None = None,
        log_file: str | None = None,
    ):
        """Initialize the session manager.

        Args:
            use_single_session: If True, all connections share one session
                               (no per-connection session IDs).
            default_config_path: Path to config file for new sessions.
            default_executable: Executable override for new sessions.
            log_file: Path to log MCP tool calls (per-session UUID file if dir).
        """
        self._registry = SessionRegistry()
        self._use_single_session = use_single_session
        self._default_config_path = default_config_path
        self._default_executable = default_executable
        self._log_file = log_file
        self._single_session_id: str | None = None
        self._single_adapter: MCPAdapter | None = None

        if use_single_session:
            self._single_session_id = self._registry.create(
                config_path=default_config_path,
                executable=default_executable,
            )

    @property
    def registry(self) -> SessionRegistry:
        """Return the session registry."""
        return self._registry

    def create_session(self, session_id: str | None = None) -> MCPAdapter:
        """Create a new session (or return existing single session).

        Args:
            session_id: If use_single_session=True, this is ignored.
                        Otherwise, a new session is created (or the existing
                        one with this ID is returned if it exists).

        Returns:
            An MCPAdapter wrapping the session.
        """
        def _make_adapter(session):
            adapter = MCPAdapter(session)
            if self._log_file:
                adapter.set_log_file(self._log_file)
            return adapter

        if self._use_single_session:
            if self._single_adapter is None:
                session = self._registry.get(self._single_session_id)
                self._single_adapter = _make_adapter(session)
            return self._single_adapter

        if session_id and session_id in self._registry._sessions:
            session = self._registry.get(session_id)
            return _make_adapter(session)

        new_id = self._registry.create(
            config_path=self._default_config_path,
            executable=self._default_executable,
        )
        session = self._registry.get(new_id)
        return _make_adapter(session)

    def get_adapter(self, session_id: str | None = None) -> MCPAdapter | None:
        """Get the MCPAdapter for a session.

        For single-session mode, returns the shared adapter.
        For multi-session mode, returns the adapter for the given session_id.
        """
        if self._use_single_session:
            if self._single_adapter is None:
                return self.create_session()
            return self._single_adapter

        if session_id is None:
            return None

        session = self._registry.get(session_id)
        if session is None:
            return None
        return MCPAdapter(session)

    def dispatch_tool(
        self, session_id: str | None, name: str, arguments: dict[str, Any] | None = None
    ) -> str:
        """Route a tool call to the correct session's adapter.

        Args:
            session_id: The session ID (None for single-session mode).
            name: The MCP tool name.
            arguments: Tool arguments.

        Returns:
            The tool result string.

        Raises:
            ValueError: If session_id is None in multi-session mode and no
                        default session exists.
            CommandError: If the tool invocation fails.
        """
        adapter = self.get_adapter(session_id)
        if adapter is None:
            raise ValueError(
                "No session found. In multi-session mode, a valid session_id is required."
            )
        return adapter.dispatch_tool(name, arguments)

    def close_session(self, session_id: str) -> bool:
        """Close a session by ID. Returns True if it existed."""
        if self._use_single_session and session_id == self._single_session_id:
            self._single_adapter = None
        return self._registry.remove(session_id)

    def list_tools(self) -> list[dict[str, Any]]:
        """Return the list of available MCP tools (same for all sessions)."""
        return TOOL_DEFINITIONS[:]

    def close(self) -> None:
        """Close all sessions and free resources."""
        self._registry.clear()
        self._single_adapter = None
        self._single_session_id = None

    def __enter__(self) -> "SessionManager":
        return self

    def __exit__(self, *args) -> None:
        self.close()
