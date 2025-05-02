#include "defines_weak.h"
#include "serialization/sdl_filesystem_defines.h"
#include <serialization/unix/unix_filesystem.h>

#ifdef _WIN32

#include <windows.h>
#include <stdio.h>

bool SDL_get_path_to__the_game(char path[1024]) {
    DWORD length = GetCurrentDirectory(1024, path);
    if (!length) 
        return false;

    return PLATFORM_access(path, IO_Access_Kind__File) == 0;
}

typedef struct PLATFORM_Directory_t {
    HANDLE handle;
} PLATFORM_Directory;

int PLATFORM_access(const char *p_c_str, IO_Access_Kind io_access_kind) {
    switch (io_access_kind) {
        default:
            DWORD fileAttr = GetFileAttributes(p_c_str);

            if (fileAttr == INVALID_FILE_ATTRIBUTES) {
                return INVALID_FILE_ATTRIBUTES;
            }
            
            return 0;
    }
}

PLATFORM_Directory *PLATFORM_opendir(const char *p_c_str) {
    WIN32_FIND_DATA findFileData;
    HANDLE hFind = FindFirstFile(p_c_str, &findFileData);

    if (hFind == INVALID_HANDLE_VALUE) {
        return 0;
    }

    PLATFORM_Directory *p_dir = malloc(sizeof(PLATFORM_Directory));
    p_dir->handle = hFind;
    return p_dir;
}

void PLATFORM_closedir(PLATFORM_Directory *p_dir) {
    if (!p_dir)
        return;

    FindClose(p_dir->handle);

    free(p_dir);
}

bool PLATFORM_mkdir(const char *p_c_str, uint32_t file_code) {
    return !CreateDirectory(p_c_str, 0);
}

Quantity__u32 PLATFORM_get_directories(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        IO_path path,
        char *p_directory_name__buffer,
        Quantity__u32 size_of__directory_name__buffer,
        Quantity__u32 max_length_of__directory_name) {
    Quantity__u32 quantity_of__directories = 0;
    WIN32_FIND_DATA findData;
    HANDLE hFind = FindFirstFile(path, &findData);

    if (hFind == INVALID_HANDLE_VALUE) {
        debug_error("SDL::WIN32::PLATFORM_get_directories, failed to find path: %s",
                path);
        return 0;
    }

    do {
        if (findData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            // Skip "." and ".."
            if (strcmp(findData.cFileName, ".") != 0 && strcmp(findData.cFileName, "..") != 0) {
                if (quantity_of__directories
                        * max_length_of__directory_name
                        > size_of__directory_name__buffer) {
                    quantity_of__directories++;
                    continue;
                }
                strncpy(directory_name__buffer
                        + sizeof(char) 
                        * max_length_of__directory_name
                        * quantity_of__directories++,
                        findData.cFileName,
                        max_length_of__directory_name);
            }
        }
    } while (FindNextFile(hFind, &findData));

    FindClose(hFind);
    return quantity_of__directories;
}

#endif
