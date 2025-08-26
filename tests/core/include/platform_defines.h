#ifndef PLATFORM_DEFINES_H
#define PLATFORM_DEFINES_H

#ifndef MAX_LENGTH_OF__IO_PATH
#define MAX_LENGTH_OF__IO_PATH 1024
#endif

#ifdef _WIN32
#ifndef PATH_SEPERATOR
#define PATH_SEPERATOR '\\'
#endif
#else
#ifndef PATH_SEPERATOR
#define PATH_SEPERATOR '/'
#endif
#endif

#ifndef CAMERA_FULCRUM__WIDTH
#define CAMERA_FULCRUM__WIDTH 256
#endif
#ifndef CAMERA_FULCRUM__HEIGHT
#define CAMERA_FULCRUM__HEIGHT 196
#endif

#ifndef MAX_QUANTITY_OF__TEXTURES
#define MAX_QUANTITY_OF__TEXTURES 128
#endif

/*****************************************************
 *  CHUNKS
 *****************************************************/

#ifndef GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS
#define GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS 4
#endif
#ifndef GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS
#define GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS 3
#endif
#ifndef GFX_CONTEXT__RENDERING_DEPTH__IN_CHUNKS
#define GFX_CONTEXT__RENDERING_DEPTH__IN_CHUNKS 1
#endif

#ifndef CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT
#define CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT 3
#endif
#ifndef CHUNK__DEPTH__BIT_SHIFT
#define CHUNK__DEPTH__BIT_SHIFT 1
#endif

#ifndef CHUNK__WIDTH
#define CHUNK__WIDTH BIT(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT)
#endif
#ifndef CHUNK__HEIGHT
#define CHUNK__HEIGHT BIT(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT)
#endif
#ifndef CHUNK__DEPTH
#define CHUNK__DEPTH BIT(CHUNK__DEPTH__BIT_SHIFT)
#endif

#ifndef CHUNK__QUANTITY_OF_TILES
#define CHUNK__QUANTITY_OF__TILES \
    (CHUNK__WIDTH * CHUNK__HEIGHT * CHUNK__DEPTH)
#endif

#ifndef TILE__WIDTH_AND__HEIGHT__BIT_SHIFT
#define TILE__WIDTH_AND__HEIGHT__BIT_SHIFT 3
#endif

#ifndef TILE__WIDTH_AND__HEIGHT_IN__PIXELS
#define TILE__WIDTH_AND__HEIGHT_IN__PIXELS \
    BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)
#endif

#ifndef LOCAL_SPACE_MANAGER__WIDTH
#define LOCAL_SPACE_MANAGER__WIDTH 8
#endif
#ifndef LOCAL_SPACE_MANAGER__HEIGHT
#define LOCAL_SPACE_MANAGER__HEIGHT 8
#endif
#ifndef LOCAL_SPACE_MANAGER__DEPTH
#define LOCAL_SPACE_MANAGER__DEPTH 1
#endif
#ifndef VOLUME_OF__LOCAL_SPACE_MANAGER
#define VOLUME_OF__LOCAL_SPACE_MANAGER\
    (LOCAL_SPACE_MANAGER__WIDTH\
    * LOCAL_SPACE_MANAGER__HEIGHT\
    * LOCAL_SPACE_MANAGER__DEPTH)
#endif

#ifndef MAX_QUANTITY_OF__CLIENTS
#define MAX_QUANTITY_OF__CLIENTS 4
#endif

#ifndef QUANTITY_OF__GLOBAL_SPACE
#define QUANTITY_OF__GLOBAL_SPACE\
    (VOLUME_OF__LOCAL_SPACE_MANAGER\
     * MAX_QUANTITY_OF__CLIENTS)
#endif

/*****************************************************
 *  ENTITIES
 *****************************************************/

#ifndef MAX_QUANTITY_OF__ENTITIES
#define MAX_QUANTITY_OF__ENTITIES 128
#endif

/*****************************************************
 *  INPUT
 *****************************************************/

#define SDL_QUANTITY_OF__INPUTS QUANTITY_OF__INPUTS + 1
#define SDL_INPUT_CODE_EQUIP QUANTITY_OF__INPUTS
#define SDL_INPUT_EQUIP BIT(QUANTITY_OF__INPUTS)

/*****************************************************
 *  TILES
 *****************************************************/

/*****************************************************
 *  GFX_CONTEXT
 *****************************************************/

/*****************************************************
 *  TEXTURES
 *****************************************************/

/*****************************************************
 *  SPRITES
 *****************************************************/

#ifndef UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT
#define UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT 3
#endif

#ifndef UI_TILE__WIDTH_AND__HEIGHT_IN__PIXELS
#define UI_TILE__WIDTH_AND__HEIGHT_IN__PIXELS \
    BIT(UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)
#endif

#ifndef UI_TILE_MAP__SMALL__MAX_QUANTITY_OF
#define UI_TILE_MAP__SMALL__MAX_QUANTITY_OF 32
#endif
#ifndef UI_TILE_MAP__SMALL__WIDTH
#define UI_TILE_MAP__SMALL__WIDTH 8
#endif
#ifndef UI_TILE_MAP__SMALL__HEIGHT
#define UI_TILE_MAP__SMALL__HEIGHT 8
#endif

#ifndef UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF
#define UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF 16
#endif
#ifndef UI_TILE_MAP__MEDIUM__WIDTH
#define UI_TILE_MAP__MEDIUM__WIDTH 16
#endif
#ifndef UI_TILE_MAP__MEDIUM__HEIGHT
#define UI_TILE_MAP__MEDIUM__HEIGHT 16
#endif

#ifndef UI_TILE_MAP__LARGE__MAX_QUANTITY_OF
#define UI_TILE_MAP__LARGE__MAX_QUANTITY_OF 8
#endif
#ifndef UI_TILE_MAP__LARGE__WIDTH
#define UI_TILE_MAP__LARGE__WIDTH 32
#endif
#ifndef UI_TILE_MAP__LARGE__HEIGHT
#define UI_TILE_MAP__LARGE__HEIGHT 32
#endif

/*****************************************************
 *  SDL
 *****************************************************/

#define TEXTURE_FLAG__FORMAT__RGB888 \
    TEXTURE_FLAG__FORMAT__1
#define TEXTURE_FLAG__FORMAT__RGBA8888 \
    TEXTURE_FLAG__FORMAT__2

#define TEXTURE_FLAG__SDL_FLAGS__BIT_COUNT 8
#define TEXTURE_FLAG__BIT_SHIFT__SDL_FLAGS \
    TEXTURE_FLAG__BIT_SHIFT__GENERAL_FLAGS

#ifndef PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF
#define PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF 128
#endif

#endif
