#ifndef NO_GUI_DEFINES_H
#define NO_GUI_DEFINES_H

#include "defines_weak.h"
#include "platform_defaults.h"
#include <defines.h>
#include <netinet/in.h>
#include <platform_defines.h>

#define TO_STRING(x) #x
#define TO_STRING_EXPANDED(x) TO_STRING(x)

#ifndef NDEBUG
#define NO_GUI_ASSERT_HOOK_NULL(\
        callee,\
        p_PLATFORM_gfx_context,\
        f_hook)\
        (!p_PLATFORM_gfx_context\
                ->NO_GUI_gfx_sub_context__wrapper\
                .f_hook)

#define NO_GUI_DEBUG_ABORT_IF__HOOK_NULL(\
        callee,\
        p_PLATFORM_gfx_context,\
        f_hook)\
        if NO_GUI_ASSERT_HOOK_NULL(callee, p_PLATFORM_gfx_context, f_hook) {\
            debug_warning("Did you forget to initialize a NO_GUI graphics backend?");\
            debug_abort("NO_GUI::" TO_STRING_EXPANDED(callee) ", " TO_STRING_EXPANDED(f_hook) " == 0.");\
            return;\
        }
#else
#define NO_GUI_ASSERT_HOOK_NULL(\
        callee,\
        p_PLATFORM_gfx_context,\
        f_hook)

#define NO_GUI_DEBUG_ABORT_IF__HOOK_NULL(\
        callee,\
        p_PLATFORM_gfx_context,\
        f_hook)
#endif

// #define MAX_LENGTH_OF__NO_GUI_TEXTURE_STRING 32
// typedef char Texture_String[
//     MAX_LENGTH_OF__NO_GUI_TEXTURE_STRING];
// typedef const char NO_GUI_Texture_String__Const[
//     MAX_LENGTH_OF__NO_GUI_TEXTURE_STRING];
// 
// typedef enum NO_GUI_Texture_Access_Kind {
//     NO_GUI_Texture_Access_Kind__None,
//     NO_GUI_Texture_Access_Kind__Static,
//     NO_GUI_Texture_Access_Kind__Streaming,
//     NO_GUI_Texture_Access_Kind__Target,
//     NO_GUI_Texture_Access_Kind__Unknown,
// } NO_GUI_Texture_Access_Kind;

typedef struct PLATFORM_Texture_t {
    u8 byte;
} PLATFORM_Texture;

typedef struct PLATFORM_Graphics_Window_t {
    u8 byte;
} PLATFORM_Graphics_Window;

typedef struct NO_GUI_Gfx_Window_Mananger_t {
    u8 byte;
} NO_GUI_Gfx_Window_Manager;

typedef struct PLATFORM_Sprite_t {
    u8 byte;
} PLATFORM_Sprite;

typedef struct SLD_Texture_Manager_t {
    u8 byte;
} NO_GUI_Texture_Manager;

typedef struct NO_GUI_Sprite_Manager_t {
    u8 byte;
} NO_GUI_Sprite_Manager;

typedef struct PLATFORM_Gfx_Context_t {
    u8 byte;
} PLATFORM_Gfx_Context;

typedef struct PLATFORM_Audio_Context_t {
    u8 byte;
} PLATFORM_Audio_Context;

#define MAX_QUANTITY_OF__SERIALIZATION_REQUESTS 256

typedef struct PLATFORM_File_System_Context_t {
    Serialization_Request NO_GUI_serialization_requests[
        MAX_QUANTITY_OF__SERIALIZATION_REQUESTS];
    IO_path path_to__base_directory;
    Quantity__u32 size_of__path_to__base_directory;
} PLATFORM_File_System_Context;

typedef struct PLATFORM_TCP_Socket_t {
    struct sockaddr_in addr_in;
    u32 socket_handle;
} PLATFORM_TCP_Socket;

typedef struct PLATFORM_TCP_Context_t {
    PLATFORM_TCP_Socket PLATFORM_tcp_sockets[
        MAX_QUANTITY_OF__TCP_SOCKETS];
} PLATFORM_TCP_Context;

#endif
