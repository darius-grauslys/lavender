#ifndef UNIX_FILESYSTEM_H
#define UNIX_FILESYSTEM_H

#include <no_gui_defines.h>
#include <serialization/no_gui_filesystem_defines.h>

bool UNIX_get_path_to__the_game(char path[1024]);

bool UNIX_get_path_to__assets(
        Asset_Directory_Kind the_kind_of__asset_directory,
        char path[1024]);

#endif
