#include "defines_weak.h"
#include "serialization/sdl_filesystem_defines.h"
#include <serialization/unix/unix_filesystem.h>
#include <string.h>

#ifdef __unix__

#include <stdio.h>
#include <dirent.h>
#include <unistd.h>
#include <libgen.h>
#include <sys/stat.h>

bool SDL_get_path_to__the_game(char path[1024]) {
    bool result = (bool)(uint64_t)realpath("/proc/self/exe", path);
    if (!result) return false;
    dirname(path);
    return access(path, F_OK) == 0;
}

typedef struct PLATFORM_Directory_t {
    DIR *p_UNIX_dir;
} PLATFORM_Directory;

int PLATFORM_access(const char *p_c_str, IO_Access_Kind io_access_kind) {
    switch (io_access_kind) {
        default:
            // TODO: impl the cases
            return access(p_c_str, F_OK);
    }
}

PLATFORM_Directory *PLATFORM_opendir(const char *p_c_str) {
    DIR *p_UNIX_dir = opendir(p_c_str);
    if (!p_UNIX_dir)
        return 0;
    PLATFORM_Directory *p_dir = malloc(sizeof(PLATFORM_Directory));
    p_dir->p_UNIX_dir = p_UNIX_dir;
    return p_dir;
}

void PLATFORM_closedir(PLATFORM_Directory *p_dir) {
    if (!p_dir)
        return;

    closedir(p_dir->p_UNIX_dir);

    free(p_dir);
}

bool PLATFORM_mkdir(const char *p_c_str, uint32_t file_code) {
    return mkdir(p_c_str, file_code);
}

Quantity__u32 PLATFORM_get_directories(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        IO_path path,
        char *p_directory_name__buffer,
        Quantity__u32 size_of__directory_name__buffer,
        Quantity__u32 max_length_of__directory_name) {
    DIR *p_dir = opendir(path);
    if (!p_dir) {
        debug_error("SDL::UNIX::PLATFORM_get_directories, failed to find path: %s",
                path);
        return 0;
    }

    Quantity__u32 quantity_of__directories = 0;

    struct dirent *p_directory_entry;

    while ((p_directory_entry = readdir(p_dir))) {
        if (!strncmp(p_directory_entry->d_name, ".", 1)
                || !strncmp(p_directory_entry->d_name, "..", 2)) {
            continue;
        }
        if (max_length_of__directory_name
                * quantity_of__directories
                > size_of__directory_name__buffer) {
            quantity_of__directories++;
            continue;
        }

        strncpy(
                p_directory_name__buffer
                + sizeof(char)
                * max_length_of__directory_name
                * quantity_of__directories++, 
                p_directory_entry->d_name, 
                max_length_of__directory_name);
    }

    return quantity_of__directories;
}

#endif
