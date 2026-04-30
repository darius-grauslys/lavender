from unittest.mock import MagicMock, patch
import pytest
import os
import json
from pathlib import Path

from lavender_tools.scan_ui import run as scan_ui_run
from lavender_tools.scan_entity import run as scan_entity_run
from lavender_tools.scan_scene import run as scan_scene_run

# --- Helper functions for file creation ---

def create_fake_file(base_dir: Path, rel_path: str, content: str):
    full_path = base_dir / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)
    return full_path


@pytest.fixture
def mock_clang():
    with patch("lavender_tools.scan_ui.get_session") as mock_ui_get_session, \
         patch("lavender_tools.scan_entity.get_session") as mock_entity_get_session, \
         patch("lavender_tools.scan_scene.get_session") as mock_scene_get_session, \
         patch("lavender_tools.clang_tools.search_workspace_symbols") as mock_search:
        
        mock_session = MagicMock()
        mock_ui_get_session.return_value = mock_session
        mock_entity_get_session.return_value = mock_session
        mock_scene_get_session.return_value = mock_session
        
        # Default behavior: symbol found
        mock_search.return_value = "Function some_func /file.c:10:1"
        
        # Return something to indicate we can control get_session for testing no session
        yield {"ui": mock_ui_get_session, "entity": mock_entity_get_session, "scene": mock_scene_get_session}, mock_search


class TestScanUi:
    @pytest.fixture
    def setup_ui_project(self, tmp_path):
        # Create necessary files for scan_ui
        create_fake_file(
            tmp_path, 
            "core/source/ui/implemented/ui_window_registrar.c", 
            "// GEN-BEGIN\nregister_ui_window_test();\n// GEN-END"
        )
        create_fake_file(
            tmp_path,
            "assets/ui/xml/test/test_window.xml",
            """<?xml version="1.0" ?>
            <ui_window>
              <config>
                <ui_func_signature for="button" c_signatures="initialize_ui_element_as__button" />
                <ui_func_signature for="grid" c_signatures="" />
                <ui_func_signature for="custom" c_signatures="my_custom_handler" />
              </config>
              <button />
              <custom />
            </ui_window>"""
        )
        return tmp_path

    def test_happy_path(self, setup_ui_project, mock_clang):
        sessions, mock_search = mock_clang
        
        result = scan_ui_run(str(setup_ui_project))
        
        assert result["summary"]["errors"] == 0
        assert result["summary"]["passed"] > 0
        assert "results" in result

    def test_missing_handler(self, setup_ui_project, mock_clang):
        sessions, mock_search = mock_clang
        # Make clangd return not found
        mock_search.return_value = "No symbols found."
        
        result = scan_ui_run(str(setup_ui_project))
        
        assert result["summary"]["errors"] > 0
        # The XML specifies two handlers that need checking, both will fail if search returns "No symbols found."
        assert any(r["status"] == "error" for r in result["results"])

    def test_no_xml_files(self, tmp_path, mock_clang):
        # Empty project, no assets/ui/xml/
        result = scan_ui_run(str(tmp_path))
        
        assert result["summary"]["total_checked"] == 0
        assert result["summary"]["errors"] == 0

    def test_output_file_written(self, setup_ui_project, mock_clang):
        output_file = setup_ui_project / "out.json"
        
        result = scan_ui_run(str(setup_ui_project), str(output_file))
        
        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
            assert "summary" in data


class TestScanEntity:
    @pytest.fixture
    def setup_entity_project(self, tmp_path):
        create_fake_file(
            tmp_path,
            "core/include/types/implemented/entity/entity_kind.h",
            """#ifndef ENTITY_KIND_H
            #define ENTITY_KIND_H
            enum {
                Entity_Kind__None,
                // GEN-BEGIN
                Entity_Kind__Player,
                Entity_Kind__Goblin,
                // GEN-END
                Entity_Kind__Count,
            };
            #endif"""
        )
        create_fake_file(
            tmp_path,
            "core/include/types/implemented/rendering/sprite/sprite_kind.h",
            """// GEN-BEGIN
            Sprite_Kind__Player,
            Sprite_Kind__Goblin,
            // GEN-END"""
        )
        create_fake_file(
            tmp_path,
            "core/source/entity/implemented/entity_registrar.c",
            """#include "entity_registrar.h"
            void register_entities(Entity_Manager *p_manager) {
                // GEN-BEGIN
                register_entity_player_into__entity_manager(p_manager);
                register_entity_goblin_into__entity_manager(p_manager);
                // GEN-END
            }"""
        )
        return tmp_path

    def test_happy_path(self, setup_entity_project, mock_clang):
        sessions, mock_search = mock_clang
        
        result = scan_entity_run(str(setup_entity_project))
        
        assert result["summary"]["errors"] == 0
        assert result["summary"]["passed"] > 0

    def test_missing_lifecycle_handler(self, setup_entity_project, mock_clang):
        sessions, mock_search = mock_clang
        mock_search.return_value = "No symbols found."
        
        result = scan_entity_run(str(setup_entity_project))
        
        assert result["summary"]["errors"] > 0
        assert any(r["status"] == "error" for r in result["results"])

    def test_empty_enum(self, tmp_path, mock_clang):
        create_fake_file(
            tmp_path,
            "core/include/types/implemented/entity/entity_kind.h",
            "// GEN-BEGIN\n// GEN-END"
        )
        create_fake_file(
            tmp_path,
            "core/source/entity/implemented/entity_registrar.c",
            ""
        )
        result = scan_entity_run(str(tmp_path))
        
        assert result["summary"]["total_checked"] == 0
        
    def test_missing_registrar(self, setup_entity_project, mock_clang):
        sessions, mock_search = mock_clang
        # Remove the registrar
        (setup_entity_project / "core/source/entity/implemented/entity_registrar.c").unlink()
        
        result = scan_entity_run(str(setup_entity_project))
        
        assert result["summary"]["errors"] > 0
        assert any(r["status"] == "error" for r in result["results"])


class TestScanScene:
    @pytest.fixture
    def setup_scene_project(self, tmp_path):
        create_fake_file(
            tmp_path,
            "core/include/types/implemented/scene/scene_kind.h",
            """#ifndef SCENE_KIND_H
            #define SCENE_KIND_H
            enum {
                Scene_Kind__None,
                // GEN-BEGIN
                Scene_Kind__Main,
                Scene_Kind__World,
                // GEN-END
                Scene_Kind__Count,
            };
            #endif"""
        )
        create_fake_file(
            tmp_path,
            "core/source/scene/implemented/scene_registrar.c",
            """// GEN-BEGIN
            register_scene__main(p_manager);
            register_scene__world(p_manager);
            // GEN-END"""
        )
        return tmp_path

    def test_happy_path(self, setup_scene_project, mock_clang):
        sessions, mock_search = mock_clang
        
        result = scan_scene_run(str(setup_scene_project))
        
        assert result["summary"]["errors"] == 0
        assert result["summary"]["passed"] > 0

    def test_missing_scene_handler(self, setup_scene_project, mock_clang):
        sessions, mock_search = mock_clang
        mock_search.return_value = "No symbols found."
        
        result = scan_scene_run(str(setup_scene_project))
        
        assert result["summary"]["errors"] > 0

    def test_registrar_mismatch(self, setup_scene_project, mock_clang):
        # Edit registrar so it is missing an entry
        create_fake_file(
            setup_scene_project,
            "core/source/scene/implemented/scene_registrar.c",
            "// GEN-BEGIN\nregister_scene__main(p_manager);\n// GEN-END"
        )
        result = scan_scene_run(str(setup_scene_project))
        
        assert result["summary"]["errors"] > 0
        assert any(r["status"] == "error" and "scene_registrar" in r.get("message", "") for r in result["results"])

    def test_no_session(self, setup_scene_project, mock_clang):
        sessions, mock_search = mock_clang
        sessions["scene"].return_value = None
        
        result = scan_scene_run(str(setup_scene_project))
        
        assert result["summary"]["warnings"] > 0
        assert any("clangd" in r["message"].lower() for r in result["results"] if r["status"] == "warning")

from lavender_tools.scan_textures import run as scan_textures_run
from lavender_tools.scan_game_actions import run as scan_game_actions_run

class TestScanTextures:
    @pytest.fixture
    def setup_texture_project(self, tmp_path):
        create_fake_file(
            tmp_path,
            "core/source/rendering/implemented/aliased_texture_registrar.c",
            """// GEN-EXTERN-BEGIN
            extern const char* name_of__texture__player;
            extern const char* name_of__texture__ground;
            const char path_to__texture__player[] = "assets/entities/player.png";
            const char path_to__texture__ground[] = "assets/world/ground.png";
            // GEN-EXTERN-END"""
        )
        create_fake_file(tmp_path, "assets/entities/player.png", "fake png data")
        create_fake_file(tmp_path, "assets/world/ground.png", "fake png data")
        return tmp_path

    @pytest.fixture
    def mock_clang_textures(self):
        with patch("lavender_tools.scan_textures.get_session") as mock_get_session, \
             patch("lavender_tools.clang_tools.search_workspace_symbols") as mock_search, \
             patch("lavender_tools.clang_tools.find_references") as mock_refs:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            
            # Default behavior: symbol found, references found
            mock_search.return_value = "Symbol found at /file.c:10:1"
            mock_refs.return_value = "Reference found at /other_file.c:10"
            yield {"session": mock_get_session, "search": mock_search, "refs": mock_refs}

    def test_happy_path(self, setup_texture_project, mock_clang_textures):
        mock_env = mock_clang_textures
        
        result = scan_textures_run(str(setup_texture_project))
        
        assert result["summary"]["errors"] == 0
        assert result["summary"]["warnings"] == 0
        assert result["summary"]["passed"] == 4

    def test_orphan_detected(self, setup_texture_project, mock_clang_textures):
        mock_env = mock_clang_textures
        # Make clangd return not found for references
        mock_env["refs"].return_value = "No references found."
        
        result = scan_textures_run(str(setup_texture_project))
        
        assert result["summary"]["warnings"] == 2
        assert result["summary"]["passed"] == 2
        assert any(r["status"] == "warning" for r in result["results"])

    def test_missing_png(self, setup_texture_project, mock_clang_textures):
        mock_env = mock_clang_textures
        # Remove a PNG file
        (setup_texture_project / "assets/entities/player.png").unlink()
        
        result = scan_textures_run(str(setup_texture_project))
        
        assert result["summary"]["errors"] > 0
        assert any(r["status"] == "error" and "exist on disk" in r.get("message", "") for r in result["results"])

    def test_no_textures_registered(self, tmp_path, mock_clang_textures):
        create_fake_file(
            tmp_path,
            "core/source/rendering/implemented/aliased_texture_registrar.c",
            "// GEN-EXTERN-BEGIN\n// GEN-EXTERN-END"
        )
        result = scan_textures_run(str(tmp_path))
        
        assert result["summary"]["total_checked"] == 0


class TestScanGameActions:
    @pytest.fixture
    def setup_game_action_project(self, tmp_path):
        create_fake_file(
            tmp_path,
            "core/include/types/implemented/game_action/game_action_kind.h",
            """#ifndef GAME_ACTION_KIND_H
            #define GAME_ACTION_KIND_H
            enum {
                Game_Action_Kind__None,
                // GEN-BEGIN
                Game_Action_Kind__Jump,
                Game_Action_Kind__Attack,
                // GEN-END
                Game_Action_Kind__Count,
            };
            #endif"""
        )
        create_fake_file(
            tmp_path,
            "core/source/game_action/implemented/game_action_registrar.c",
            """// GEN-BEGIN
            register_game_action__jump(p_manager);
            register_game_action__attack(p_manager);
            // GEN-END"""
        )
        return tmp_path

    @pytest.fixture
    def mock_clang_game_actions(self):
        with patch("lavender_tools.scan_game_actions.get_session") as mock_get_session, \
             patch("lavender_tools.clang_tools.search_workspace_symbols") as mock_search:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            
            # Default behavior: handlers found
            mock_search.return_value = "Function some_func /file.c:10:1"
            yield {"session": mock_get_session, "search": mock_search}

    def test_happy_path(self, setup_game_action_project, mock_clang_game_actions):
        mock_env = mock_clang_game_actions
        
        result = scan_game_actions_run(str(setup_game_action_project))
        
        assert result["summary"]["errors"] == 0
        assert result["summary"]["passed"] == 5
        assert result["summary"]["warnings"] == 1

    def test_missing_handler(self, setup_game_action_project, mock_clang_game_actions):
        mock_env = mock_clang_game_actions
        # Make clangd return not found
        mock_env["search"].return_value = "No symbols found."
        
        result = scan_game_actions_run(str(setup_game_action_project))
        
        assert result["summary"]["errors"] == 3
        assert result["summary"]["passed"] == 2
        assert result["summary"]["warnings"] == 1
        assert any(r["status"] == "error" for r in result["results"])

    def test_empty_enum(self, tmp_path, mock_clang_game_actions):
        create_fake_file(
            tmp_path,
            "core/include/types/implemented/game_action/game_action_kind.h",
            "// GEN-BEGIN\n// GEN-END"
        )
        create_fake_file(
            tmp_path,
            "core/source/game_action/implemented/game_action_registrar.c",
            ""
        )
        result = scan_game_actions_run(str(tmp_path))
        
        assert result["summary"]["total_checked"] == 0

    def test_output_path(self, setup_game_action_project, mock_clang_game_actions):
        output_file = setup_game_action_project / "out.json"
        
        result = scan_game_actions_run(str(setup_game_action_project), str(output_file))
        
        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
            assert "summary" in data
