"""test_scan_path_fallback.py — Unit tests for path fallback in scan tools.

Tests verify that scan_scene, scan_entity, and scan_ui correctly resolve
files in both primary (root include/source) and fallback (core/) layouts,
and gracefully handle missing files.
"""

import pytest
from unittest.mock import patch

from lavender_tools import scan_scene, scan_entity, scan_ui


@pytest.fixture(autouse=True)
def mock_clangd_session():
    with patch("lavender_tools.scan_scene.get_session", return_value=None), \
         patch("lavender_tools.scan_entity.get_session", return_value=None), \
         patch("lavender_tools.scan_ui.get_session", return_value=None):
        yield


# ---------------------------------------------------------------------------
# scan_scene fixtures
# ---------------------------------------------------------------------------

def _setup_scene_primary(tmp_path):
    include = tmp_path / "include" / "types" / "implemented" / "scene"
    source = tmp_path / "source" / "scene" / "implemented"
    include.mkdir(parents=True)
    source.mkdir(parents=True)

    (include / "scene_kind.h").write_text(
        "// GEN-BEGIN\n"
        "Scene_Kind__Main\n"
        "Scene_Kind__World\n"
        "// GEN-END\n"
    )
    (source / "scene_registrar.c").write_text(
        "// GEN-BEGIN\n"
        "register_scene__main\n"
        "register_scene__world\n"
        "// GEN-END\n"
    )
    (source / "scene__main.c").write_text(
        "void foo() {\n"
        "    UI_Window_Kind__Test;\n"
        "    Scene_Kind__Other;\n"
        "}\n"
    )


def _setup_scene_fallback(tmp_path):
    include = tmp_path / "core" / "include" / "types" / "implemented" / "scene"
    source = tmp_path / "core" / "source" / "scene" / "implemented"
    include.mkdir(parents=True)
    source.mkdir(parents=True)

    (include / "scene_kind.h").write_text(
        "// GEN-BEGIN\n"
        "Scene_Kind__Main\n"
        "Scene_Kind__World\n"
        "// GEN-END\n"
    )
    (source / "scene_registrar.c").write_text(
        "// GEN-BEGIN\n"
        "register_scene__main\n"
        "register_scene__world\n"
        "// GEN-END\n"
    )
    (source / "scene__main.c").write_text(
        "void foo() {\n"
        "    UI_Window_Kind__Test;\n"
        "    Scene_Kind__Other;\n"
        "}\n"
    )


# ---------------------------------------------------------------------------
# scan_entity fixtures
# ---------------------------------------------------------------------------

def _setup_entity_primary(tmp_path):
    entity_include = tmp_path / "include" / "types" / "implemented" / "entity"
    entity_source = tmp_path / "source" / "entity" / "implemented"
    sprite_include = tmp_path / "include" / "types" / "implemented" / "rendering" / "sprite"
    entity_include.mkdir(parents=True)
    entity_source.mkdir(parents=True)
    sprite_include.mkdir(parents=True)

    (entity_include / "entity_kind.h").write_text(
        "// GEN-BEGIN\n"
        "Entity_Kind__Player\n"
        "// GEN-END\n"
    )
    (entity_source / "entity_registrar.c").write_text(
        "// GEN-BEGIN\n"
        "register_entity_player_into__entity_manager\n"
        "// GEN-END\n"
    )
    (sprite_include / "sprite_kind.h").write_text(
        "// GEN-BEGIN\n"
        "Sprite_Kind__Player\n"
        "// GEN-END\n"
    )


def _setup_entity_fallback(tmp_path):
    entity_include = tmp_path / "core" / "include" / "types" / "implemented" / "entity"
    entity_source = tmp_path / "core" / "source" / "entity" / "implemented"
    sprite_include = tmp_path / "core" / "include" / "types" / "implemented" / "rendering" / "sprite"
    entity_include.mkdir(parents=True)
    entity_source.mkdir(parents=True)
    sprite_include.mkdir(parents=True)

    (entity_include / "entity_kind.h").write_text(
        "// GEN-BEGIN\n"
        "Entity_Kind__Player\n"
        "// GEN-END\n"
    )
    (entity_source / "entity_registrar.c").write_text(
        "// GEN-BEGIN\n"
        "register_entity_player_into__entity_manager\n"
        "// GEN-END\n"
    )
    (sprite_include / "sprite_kind.h").write_text(
        "// GEN-BEGIN\n"
        "Sprite_Kind__Player\n"
        "// GEN-END\n"
    )


# ---------------------------------------------------------------------------
# scan_ui fixtures
# ---------------------------------------------------------------------------

def _setup_ui_primary(tmp_path):
    xml_dir = tmp_path / "assets" / "ui" / "xml"
    source_dir = tmp_path / "source" / "ui" / "implemented"
    xml_dir.mkdir(parents=True)
    source_dir.mkdir(parents=True)

    (xml_dir / "test.xml").write_text(
        "<ui>\n"
        "  <config>\n"
        "    <output c_path=\"./source/ui/implemented/generated/game/test.c\"/>\n"
        "  </config>\n"
        "</ui>\n"
    )
    (source_dir / "ui_window_registrar.c").write_text(
        "// GEN-BEGIN\n"
        "register_ui_window_into__ui_window_manager_as__test\n"
        "// GEN-END\n"
    )


def _setup_ui_fallback(tmp_path):
    source_dir = tmp_path / "core" / "source" / "ui" / "implemented"
    source_dir.mkdir(parents=True)

    (source_dir / "ui_window_registrar.c").write_text(
        "// GEN-BEGIN\n"
        "register_ui_window_into__ui_window_manager_as__test\n"
        "// GEN-END\n"
    )


# ---------------------------------------------------------------------------
# scan_scene tests
# ---------------------------------------------------------------------------

def test_scan_scene_finds_primary_layout(tmp_path):
    """Files at root include/source are found and parsed."""
    _setup_scene_primary(tmp_path)
    result = scan_scene.run(str(tmp_path))

    assert result["tool"] == "scan_scene"
    assert result["project_root"] == str(tmp_path)
    assert "timestamp" in result
    assert "summary" in result
    assert "results" in result

    assert result["summary"]["total_checked"] > 0
    assert result["summary"]["passed"] > 0
    assert result["summary"]["errors"] == 0


def test_scan_scene_finds_fallback_layout(tmp_path):
    """Files only under core/ are discovered via fallback paths."""
    _setup_scene_fallback(tmp_path)
    result = scan_scene.run(str(tmp_path))

    assert result["summary"]["total_checked"] > 0
    assert result["summary"]["passed"] > 0
    assert result["summary"]["errors"] == 0


def test_scan_scene_graceful_when_missing(tmp_path):
    """Empty project produces no checks and only the clangd warning."""
    result = scan_scene.run(str(tmp_path))

    assert result["tool"] == "scan_scene"
    assert result["summary"]["total_checked"] == 0
    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 1
    assert any("clangd not configured" in r["message"] for r in result["results"])


# ---------------------------------------------------------------------------
# scan_entity tests
# ---------------------------------------------------------------------------

def test_scan_entity_finds_primary_layout(tmp_path):
    """Files at root include/source are found and parsed."""
    _setup_entity_primary(tmp_path)
    result = scan_entity.run(str(tmp_path))

    assert result["tool"] == "scan_entity"
    assert result["project_root"] == str(tmp_path)
    assert "timestamp" in result
    assert "summary" in result
    assert "results" in result

    assert result["summary"]["total_checked"] > 0
    assert result["summary"]["passed"] > 0
    assert result["summary"]["errors"] == 0


def test_scan_entity_finds_fallback_layout(tmp_path):
    """Files only under core/ are discovered via fallback paths."""
    _setup_entity_fallback(tmp_path)
    result = scan_entity.run(str(tmp_path))

    assert result["summary"]["total_checked"] > 0
    assert result["summary"]["passed"] > 0
    assert result["summary"]["errors"] == 0


def test_scan_entity_graceful_when_missing(tmp_path):
    """Empty project produces no checks and only the clangd warning."""
    result = scan_entity.run(str(tmp_path))

    assert result["tool"] == "scan_entity"
    assert result["summary"]["total_checked"] == 0
    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 1
    assert any("clangd not configured" in r["message"] for r in result["results"])


# ---------------------------------------------------------------------------
# scan_ui tests
# ---------------------------------------------------------------------------

def test_scan_ui_finds_primary_layout(tmp_path):
    """Files at root are found; matching XML and registrar produce no mismatch."""
    _setup_ui_primary(tmp_path)
    result = scan_ui.run(str(tmp_path))

    assert result["tool"] == "scan_ui"
    assert result["project_root"] == str(tmp_path)
    assert "timestamp" in result
    assert "summary" in result
    assert "results" in result

    assert result["summary"]["errors"] == 0
    # With matching XML/registrar and no handler signatures, the only warning is clangd.
    assert result["summary"]["warnings"] == 1


def test_scan_ui_finds_fallback_layout(tmp_path):
    """Registrar under core/ is discovered via fallback path."""
    _setup_ui_fallback(tmp_path)
    result = scan_ui.run(str(tmp_path))

    assert result["summary"]["total_checked"] > 0
    assert result["summary"]["errors"] == 0
    # Expect clangd warning plus registrar-without-XML warning.
    assert result["summary"]["warnings"] > 1
    assert any("no corresponding XML" in r["message"] for r in result["results"])


def test_scan_ui_graceful_when_missing(tmp_path):
    """Empty project produces no checks and only the clangd warning."""
    result = scan_ui.run(str(tmp_path))

    assert result["tool"] == "scan_ui"
    assert result["summary"]["total_checked"] == 0
    assert result["summary"]["errors"] == 0
    assert result["summary"]["warnings"] == 1
    assert any("clangd not configured" in r["message"] for r in result["results"])
