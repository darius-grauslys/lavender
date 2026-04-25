"""Tests for workspace movement."""

from workspace.movement import WorkspaceMovement, ViewportState


class TestWorkspaceMovement:
    def test_initial_state(self):
        m = WorkspaceMovement()
        assert m.viewport.center_x == 0
        assert m.viewport.center_y == 0
        assert m.viewport.center_z == 0

    def test_pan_by_tiles(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(3, -2)
        assert m.viewport.center_x == 3
        assert m.viewport.center_y == -2

    def test_pan_by_chunks(self):
        m = WorkspaceMovement()
        m.pan_by_chunks(1, 1, chunk_width=8, chunk_height=8)
        assert m.viewport.center_x == 8
        assert m.viewport.center_y == 8

    def test_move_z(self):
        m = WorkspaceMovement()
        m.move_z(1)
        assert m.viewport.center_z == 1
        m.move_z(-2)
        assert m.viewport.center_z == -1

    def test_go_to(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(100, 100)
        m.go_to(5, 10, 2)
        assert m.viewport.center_x == 5
        assert m.viewport.center_y == 10
        assert m.viewport.center_z == 2
        assert m.viewport.offset_x == 0.0
        assert m.viewport.offset_y == 0.0
