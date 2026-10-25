"""Entry point: python3 -m mcp_layered --stdio"""

import sys

from mcp_layered.layer_lav_mcp_server import main

if __name__ == "__main__":
    sys.exit(main())
