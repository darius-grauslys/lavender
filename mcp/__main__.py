"""Entry point: python3 -m mcp.lav_mcp_server --port 8890"""

import sys

from .lav_mcp_server import main

if __name__ == "__main__":
    sys.exit(main())
