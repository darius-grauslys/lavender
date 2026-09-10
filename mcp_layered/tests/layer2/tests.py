"""Tests for Layer 2 (layer_lav_config.py).

Run: python3 mcp_layered/tests/layer2/tests.py
"""

import os
import sys
import tempfile
import unittest

# Setup import paths
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.layer_lav_config import (
    LavConfig,
    DEFAULT_EXECUTABLE,
    DEFAULT_CORE_DUMP_DIR,
    DEFAULT_SCREENSHOT_DIR,
    default_config,
    load_config,
    save_config,
)


class TestLavConfigDefaults(unittest.TestCase):
    """Test default configuration values."""

    def test_default_config(self):
        """default_config() returns expected defaults."""
        config = default_config()
        self.assertEqual(config.executable, DEFAULT_EXECUTABLE)
        self.assertEqual(config.core_dump_dir, DEFAULT_CORE_DUMP_DIR)
        self.assertEqual(config.screenshot_dir, DEFAULT_SCREENSHOT_DIR)
        self.assertEqual(config.gdb_path, "gdb")
        self.assertIsInstance(config.gdb_args, list)
        self.assertEqual(config.gdb_args, ["--nx", "--quiet", "--interpreter=mi3"])
        self.assertEqual(config.env, {})

    def test_config_dataclass_defaults(self):
        """LavConfig() with no args uses defaults."""
        config = LavConfig()
        self.assertEqual(config.executable, DEFAULT_EXECUTABLE)
        self.assertEqual(config.log_file, "/tmp/lav-log/")


class TestLavConfigCreation(unittest.TestCase):
    """Test creating LavConfig with custom values."""

    def test_custom_executable(self):
        """Custom executable path is stored."""
        config = LavConfig(executable="/custom/game")
        self.assertEqual(config.executable, "/custom/game")

    def test_custom_paths(self):
        """Custom core dump and screenshot dirs are stored."""
        config = LavConfig(
            core_dump_dir="/tmp/dumps/",
            screenshot_dir="/tmp/screens/"
        )
        self.assertEqual(config.core_dump_dir, "/tmp/dumps/")
        self.assertEqual(config.screenshot_dir, "/tmp/screens/")

    def test_custom_gdb_path(self):
        """Custom GDB path is stored."""
        config = LavConfig(gdb_path="/usr/local/bin/gdb")
        self.assertEqual(config.gdb_path, "/usr/local/bin/gdb")

    def test_custom_gdb_args(self):
        """Custom GDB args are stored."""
        config = LavConfig(gdb_args=["-nx", "--quiet"])
        self.assertEqual(config.gdb_args, ["-nx", "--quiet"])

    def test_custom_env(self):
        """Custom env dict is stored."""
        config = LavConfig(env={"DISPLAY": ":0", "HOME": "/home/user"})
        self.assertEqual(config.env, {"DISPLAY": ":0", "HOME": "/home/user"})

    def test_user_path_expansion(self):
        """User paths (~) are expanded."""
        config = LavConfig(
            executable="~/bin/game",
            core_dump_dir="~/dumps/",
            screenshot_dir="~/screens/"
        )
        # Check expansion happened (should not contain ~)
        self.assertNotIn("~", config.executable)
        self.assertNotIn("~", config.core_dump_dir)
        self.assertNotIn("~", config.screenshot_dir)


class TestLavConfigAliases(unittest.TestCase):
    """Test backward-compatible alias properties."""

    def test_dump_location_alias(self):
        """dump_location is an alias for core_dump_dir."""
        config = LavConfig(core_dump_dir="/tmp/test-dumps/")
        self.assertEqual(config.dump_location, "/tmp/test-dumps/")

    def test_screenshot_location_alias(self):
        """screenshot_location is an alias for screenshot_dir."""
        config = LavConfig(screenshot_dir="/tmp/test-screens/")
        self.assertEqual(config.screenshot_location, "/tmp/test-screens/")


class TestLavConfigSerialization(unittest.TestCase):
    """Test JSON serialization/deserialization."""

    def test_to_dict(self):
        """to_dict() returns all fields."""
        config = LavConfig(executable="/custom/game", gdb_path="/usr/bin/gdb")
        d = config.to_dict()
        self.assertIn("executable", d)
        self.assertIn("core_dump_dir", d)
        self.assertIn("screenshot_dir", d)
        self.assertIn("log_file", d)
        self.assertIn("gdb_path", d)
        self.assertIn("gdb_args", d)
        self.assertIn("env", d)
        self.assertEqual(d["executable"], "/custom/game")

    def test_from_dict(self):
        """from_dict() creates config from dict."""
        data = {
            "executable": "/custom/game",
            "core_dump_dir": "/tmp/dumps/",
            "gdb_args": ["-nx"],
        }
        config = LavConfig.from_dict(data)
        self.assertEqual(config.executable, "/custom/game")
        self.assertEqual(config.core_dump_dir, "/tmp/dumps/")
        self.assertEqual(config.gdb_args, ["-nx"])

    def test_from_dict_ignores_unknown(self):
        """from_dict() ignores unknown keys."""
        data = {"executable": "/test", "unknown_field": "ignored"}
        config = LavConfig.from_dict(data)
        self.assertEqual(config.executable, "/test")
        self.assertFalse(hasattr(config, "unknown_field"))

    def test_to_json_and_back(self):
        """Round-trip serialization works."""
        original = LavConfig(
            executable="/custom/game",
            gdb_args=["-nx", "--quiet"],
            env={"DISPLAY": ":0"}
        )
        json_str = original.to_json()
        restored = LavConfig.from_json(json_str)
        self.assertEqual(restored.executable, original.executable)
        self.assertEqual(restored.gdb_args, original.gdb_args)
        self.assertEqual(restored.env, original.env)


class TestConfigLoadSave(unittest.TestCase):
    """Test load_config() and save_config()."""

    def test_load_config_none_returns_defaults(self):
        """load_config(None) returns default config."""
        config = load_config(None)
        self.assertEqual(config.executable, DEFAULT_EXECUTABLE)

    def test_load_config_missing_file_returns_defaults(self):
        """load_config with nonexistent path returns defaults."""
        config = load_config("/nonexistent/path/config.json")
        self.assertEqual(config.executable, DEFAULT_EXECUTABLE)

    def test_save_and_load_config(self):
        """save_config + load_config round-trip works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = LavConfig(
                executable="/custom/game",
                gdb_args=["-nx"],
                env={"DISPLAY": ":0"}
            )
            config_path = os.path.join(tmpdir, "config.json")
            save_config(config, config_path)

            loaded = load_config(config_path)
            self.assertEqual(loaded.executable, "/custom/game")
            self.assertEqual(loaded.gdb_args, ["-nx"])
            self.assertEqual(loaded.env, {"DISPLAY": ":0"})

    def test_load_config_partial_overrides(self):
        """load_config with partial config uses defaults for missing fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save a config with only executable overridden
            config = default_config()
            config.executable = "/custom/game"
            config_path = os.path.join(tmpdir, "config.json")
            save_config(config, config_path)

            loaded = load_config(config_path)
            self.assertEqual(loaded.executable, "/custom/game")
            # Other fields should be defaults
            self.assertEqual(loaded.gdb_path, "gdb")


class TestLavConfigDirectoryManagement(unittest.TestCase):
    """Test ensure_directories() method."""

    def test_ensure_directories(self):
        """ensure_directories() creates directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dump_dir = os.path.join(tmpdir, "dumps")
            screen_dir = os.path.join(tmpdir, "screens")
            config = LavConfig(
                core_dump_dir=dump_dir,
                screenshot_dir=screen_dir,
                log_file=None
            )
            config.ensure_directories()
            self.assertTrue(os.path.isdir(dump_dir))
            self.assertTrue(os.path.isdir(screen_dir))

    def test_ensure_directories_idempotent(self):
        """ensure_directories() is idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dump_dir = os.path.join(tmpdir, "dumps")
            config = LavConfig(core_dump_dir=dump_dir, log_file=None)
            config.ensure_directories()
            config.ensure_directories()  # Should not raise
            self.assertTrue(os.path.isdir(dump_dir))


if __name__ == "__main__":
    unittest.main(verbosity=2)
