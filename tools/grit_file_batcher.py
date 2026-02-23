#
# This python file is used to organize all .png files
# found in subdirectories of a provided directory
# such that the paths are organized alphabetically
# by the file names and not by the full path.
#
# This is done so that files beginning with an
# underscore appear first on the list. Such files
# are shared ui tilesets.
#

import sys
import os
import subprocess
import shutil
from pathlib import Path

def main():
    if len(sys.argv) <= 1:
        print('Usage: python grit_file_batcher.py [path] <grit_args>')
        sys.exit(-1)
    cwd = Path.cwd()
    grit_args = sys.argv[2] if len(sys.argv) > 2 else ''
    if not os.path.exists(cwd / sys.argv[1]):
        print('Missing assets directory.')
        sys.exit(-1)

    grit_files = (cwd / 'assets').rglob('*.grit')
    grit_command_and_path_list = []

    for grit_file in grit_files:
        png_files = sorted(Path(grit_file.parent).rglob('*.png'), key=lambda file: file.name)
        if len(png_files) == 0:
            continue
        grit_command_and_path_list.append((f'grit {' '.join([str(png_file) for png_file in png_files])} -ff {grit_file} {grit_args}', png_files[0].parent))

    processes = []
    for grit_command, path in grit_command_and_path_list:
        relative_path = path.parent.relative_to(cwd) / path.name
        output_path = cwd / f'lav_gen/grit/{str(relative_path)}'
        print(output_path)
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        Path(output_path).mkdir(parents=True, exist_ok=True)
        subprocess.Popen(grit_command.split(' '), cwd=str(output_path))
    for process in processes:
        process.wait()
    
if __name__ == '__main__':
    main()
