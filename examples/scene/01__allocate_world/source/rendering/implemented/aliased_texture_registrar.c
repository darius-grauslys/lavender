#include "rendering/implemented/aliased_texture_registrar.h"
#include "game.h"
#include "rendering/aliased_texture_manager.h"

// GEN-EXTERN-BEGIN
// 1) define the alias and paths:
Texture_Name__c_str name_of__texture__tileset = "tileset";
IO_path path_to__texture__tileset = "assets/world/tileset.png";
// GEN-EXTERN-END

// TUTORIAL NOTE:
// You don't HAVE to use this function, you can make new ones
// for each individual scene! Useful if you want resources to
// only have a scene's lifecycle.
void register_aliased_textures(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Game *p_game) {
    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context =
        get_p_PLATFORM_gfx_context_from__game(p_game);
    // GEN-BEGIN
    // 2) Load the textures
    load_texture_from__path_with__alias(
            p_PLATFORM_gfx_context, 
            0, 
            p_aliased_texture_manager, 
            name_of__texture__tileset, 
            TEXTURE_FLAGS(
                TEXTURE_FLAG__SIZE_256x256, // TUTORIAL NOTE: this can be different
                TEXTURE_FLAG__RENDER_METHOD__0,
                TEXTURE_FLAG__FORMAT__RGBA8888),
            path_to__texture__tileset,
            0);
    // GEN-END
}
