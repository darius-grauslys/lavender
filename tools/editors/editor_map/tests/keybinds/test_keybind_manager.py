"""Tests for the keybind manager."""

from keybinds.keybind import KeyCombo, Modifier
from keybinds.keybind_manager import KeybindManager


class TestSetBaseKeybinds:
    def test_base_keybind_fires(self):
        mgr = KeybindManager()
        called = []
        mgr.set_base_keybinds({
            KeyCombo(65, Modifier.CTRL): lambda: called.append("a"),
        })
        assert mgr.fire(KeyCombo(65, Modifier.CTRL))
        assert called == ["a"]

    def test_unknown_combo_returns_false(self):
        mgr = KeybindManager()
        mgr.set_base_keybinds({})
        assert not mgr.fire(KeyCombo(65))


class TestPushPopOverride:
    def test_override_takes_precedence(self):
        mgr = KeybindManager()
        results = []
        mgr.set_base_keybinds({
            KeyCombo(65): lambda: results.append("base"),
        })
        mgr.push_override({
            KeyCombo(65): lambda: results.append("override"),
        })
        mgr.fire(KeyCombo(65))
        assert results == ["override"]

    def test_pop_restores_base(self):
        mgr = KeybindManager()
        results = []
        mgr.set_base_keybinds({
            KeyCombo(65): lambda: results.append("base"),
        })
        mgr.push_override({
            KeyCombo(65): lambda: results.append("override"),
        })
        mgr.pop_override()
        mgr.fire(KeyCombo(65))
        assert results == ["base"]

    def test_stacked_overrides(self):
        mgr = KeybindManager()
        results = []
        mgr.set_base_keybinds({
            KeyCombo(65): lambda: results.append("base"),
        })
        mgr.push_override({
            KeyCombo(65): lambda: results.append("o1"),
        })
        mgr.push_override({
            KeyCombo(65): lambda: results.append("o2"),
        })
        mgr.fire(KeyCombo(65))
        assert results == ["o2"]
        mgr.pop_override()
        results.clear()
        mgr.fire(KeyCombo(65))
        assert results == ["o1"]

    def test_pop_on_empty_is_safe(self):
        mgr = KeybindManager()
        mgr.pop_override()  # should not raise


class TestClearOverrideStack:
    def test_clear_restores_base(self):
        mgr = KeybindManager()
        results = []
        mgr.set_base_keybinds({
            KeyCombo(65): lambda: results.append("base"),
        })
        mgr.push_override({
            KeyCombo(65): lambda: results.append("o1"),
        })
        mgr.push_override({
            KeyCombo(65): lambda: results.append("o2"),
        })
        mgr.clear_override_stack()
        mgr.fire(KeyCombo(65))
        assert results == ["base"]


class TestGetAllActiveBinds:
    def test_includes_base_and_overrides(self):
        mgr = KeybindManager()
        mgr.set_base_keybinds({
            KeyCombo(65): lambda: None,
            KeyCombo(66): lambda: None,
        })
        mgr.push_override({
            KeyCombo(65): lambda: None,
            KeyCombo(67): lambda: None,
        })
        active = mgr.get_all_active_binds()
        assert KeyCombo(65) in active
        assert KeyCombo(66) in active
        assert KeyCombo(67) in active


class TestPartialOverride:
    def test_override_only_affects_specified_keys(self):
        mgr = KeybindManager()
        results = []
        mgr.set_base_keybinds({
            KeyCombo(65): lambda: results.append("a_base"),
            KeyCombo(66): lambda: results.append("b_base"),
        })
        mgr.push_override({
            KeyCombo(65): lambda: results.append("a_override"),
        })
        mgr.fire(KeyCombo(65))
        mgr.fire(KeyCombo(66))
        assert results == ["a_override", "b_base"]
