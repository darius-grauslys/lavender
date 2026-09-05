"""Entry point: python3 -m harness --program /path/to/executable"""

import sys

from .main import main

if __name__ == "__main__":
    sys.exit(main())
