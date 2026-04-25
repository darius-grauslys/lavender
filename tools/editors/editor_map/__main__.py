"""
Entry point for running the editor as a module:
    python -m tools.editors.editor_map --engine-dir /path/to/engine
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Lavender Map Editor")
    parser.add_argument(
        "--engine-dir",
        required=True,
        help="Path to the Lavender engine root directory")
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Path to the project directory (default: current dir)")
    args = parser.parse_args()

    import sys
    from pathlib import Path
    _editor_map_dir = str(Path(__file__).resolve().parent)
    if _editor_map_dir not in sys.path:
        sys.path.insert(0, _editor_map_dir)
    from editor_app import run_editor
    run_editor(args.engine_dir, args.project_dir)


if __name__ == "__main__":
    main()
