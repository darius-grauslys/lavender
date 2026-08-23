"""CLI entry point for running lav_impl tools from subprocess / container."""
from __future__ import annotations

import json
import sys
import traceback

from . import tools as lav_tools


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python -m lavender_tools.lav_impl <tool_name> [json_params] [project_dir]",
            file=sys.stderr,
        )
        sys.exit(1)

    tool_name = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    project_dir = sys.argv[3] if len(sys.argv) > 3 else ""

    func = getattr(lav_tools, tool_name, None)
    if func is None:
        print(f"ERROR: Unknown tool '{tool_name}'", file=sys.stderr)
        sys.exit(1)

    try:
        result = func(project_dir=project_dir, **params)
    except Exception as exc:
        print(
            f"ERROR (exit 1): {exc}\n{traceback.format_exc()}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(result)


if __name__ == "__main__":
    main()
