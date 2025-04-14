#ifndef NO_GUI_FILESYSTEM
#define NO_GUI_FILESYSTEM

#include <no_gui_defines.h>
#include <serialization/no_gui_filesystem_defines.h>

extern PLATFORM_File_System_Context __NO_GUI_file_system_context;

bool NO_GUI_get_path_to__the_game(char path[1024]);

bool NO_GUI_get_path_to__assets(
        Asset_Directory_Kind the_kind_of__asset_directory,
        char path[1024]);

void NO_GUI_poll_serialization_requests(
        Game *p_game);

void m_NO_GUI_process__serialization(
        Process *p_this_process,
        Game *p_game);

#endif
