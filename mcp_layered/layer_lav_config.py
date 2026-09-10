"""Layer 2: Configuration for the Lavender debugging system.

Provides a single ``LavConfig`` dataclass that holds all configuration:
- Executable path
- Core dump directory
- Screenshot directory  
- Log file location
- GDB executable path and args
- Environment variables

This layer is pure data/configuration — it does NOT import any other layer.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


# Default configuration values
DEFAULT_EXECUTABLE = "/home/shalidor/Projects/Projects__Lavender/AncientsGame/build/sdl/AncientsGame"
DEFAULT_CORE_DUMP_DIR = "/tmp/lav-core-dump/"
DEFAULT_SCREENSHOT_DIR = "/tmp/lav-screenshot/"
DEFAULT_LOG_FILE = "/tmp/lav-log/"
DEFAULT_GDB_PATH = "gdb"
DEFAULT_GDB_ARGS: list[str] = ["--nx", "--quiet", "--interpreter=mi3"]


@dataclass
class LavConfig:
    """Configuration for the Lavender debugging system.

    This is the single source of truth for all configuration values.
    All paths are expanded (user ~ is resolved).

    Attributes:
        executable: Path to the game executable to debug.
        core_dump_dir: Directory where core dumps are stored.
        screenshot_dir: Directory where screenshots are saved.
        log_file: Path to the MCP tool call/response log file (or directory).
        gdb_path: Path to the GDB executable.
        gdb_args: Extra arguments to pass to GDB.
        env: Environment variables to propagate to the GDB inferior process.
    """

    executable: str = DEFAULT_EXECUTABLE
    core_dump_dir: str = DEFAULT_CORE_DUMP_DIR
    screenshot_dir: str = DEFAULT_SCREENSHOT_DIR
    log_file: str | None = DEFAULT_LOG_FILE
    gdb_path: str = DEFAULT_GDB_PATH
    gdb_args: list[str] = field(default_factory=lambda: list(DEFAULT_GDB_ARGS))
    env: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Expand user paths after initialization."""
        self.executable = os.path.expanduser(self.executable)
        self.core_dump_dir = os.path.expanduser(self.core_dump_dir)
        self.screenshot_dir = os.path.expanduser(self.screenshot_dir)
        if self.log_file is not None:
            self.log_file = os.path.expanduser(self.log_file)

    # -- Convenience properties for backward compatibility aliases -- #

    @property
    def dump_location(self) -> str:
        """Alias for core_dump_dir (backward compat with mcp/)."""
        return self.core_dump_dir

    @property
    def screenshot_location(self) -> str:
        """Alias for screenshot_dir (backward compat with mcp/)."""
        return self.screenshot_dir

    # -- Serialization -- #

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (for JSON config files)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LavConfig":
        """Create from a dict, ignoring unknown keys."""
        known_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "LavConfig":
        """Parse from JSON string."""
        return cls.from_dict(json.loads(json_str))

    # -- Directory management -- #

    def ensure_directories(self) -> None:
        """Create all configured directories if they don't exist."""
        for dir_path in (self.core_dump_dir, self.screenshot_dir):
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

        # Log file might be a directory
        if self.log_file and not self.log_file.endswith(".jsonl"):
            os.makedirs(self.log_file, exist_ok=True)


def default_config() -> LavConfig:
    """Return a configuration with all default values."""
    return LavConfig()


def load_config(path: str | None = None) -> LavConfig:
    """Load configuration from a file, or return defaults if path is None.

    Supports JSON config files. Unknown fields are ignored.
    """
    if path is None:
        return default_config()

    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        return default_config()

    with open(path, "r") as f:
        data = json.load(f)

    return LavConfig.from_dict(data)


def save_config(config: LavConfig, path: str) -> None:
    """Save configuration to a JSON file."""
    path = os.path.expanduser(path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(config.to_json())
