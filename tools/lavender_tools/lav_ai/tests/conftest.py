import sys
from pathlib import Path

# Ensure lavender_tools is importable by adding the tools directory to sys.path
_tools_dir = Path(__file__).resolve().parents[4]
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))
