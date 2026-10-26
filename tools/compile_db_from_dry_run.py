#!/usr/bin/env python3
"""Turn `make -n -B` output into a compile_commands.json, compiling nothing.

    make -n -B ... | compile_db_from_dry_run.py <directory> > compile_commands.json

<directory> is where make runs the compile commands (the build dir). Each
printed line with a `-c <file>.c` becomes one entry; every other line (mkdir,
link, ...) is ignored. Used by `make compile_commands_dry`.
"""

import json
import os
import shlex
import sys


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    directory = os.path.abspath(sys.argv[1])
    entries = []
    for line in sys.stdin:
        try:
            args = shlex.split(line)
        except ValueError:
            continue
        if "-c" not in args:
            continue
        i = args.index("-c")
        if i + 1 >= len(args) or not args[i + 1].endswith(".c"):
            continue
        source = os.path.join(directory, args[i + 1])
        entries.append({"directory": directory, "arguments": args, "file": source})
    if not entries:
        sys.exit("compile_db_from_dry_run: no compile commands in the input")
    json.dump(entries, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
