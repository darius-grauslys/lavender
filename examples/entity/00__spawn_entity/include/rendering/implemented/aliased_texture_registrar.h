#ifndef ALIAS_TEXTURE_REGISTRAR_H
#define ALIAS_TEXTURE_REGISTRAR_H

#include "defines.h"

// GEN-EXTERN-BEGIN
extern Texture_Name__c_str name_of__texture__tileset;
extern IO_path path_to__texture__tileset;
extern Texture_Name__c_str name_of__texture__dummy;
extern IO_path path_to__texture__dummy;
// GEN-EXTERN-END

void register_aliased_textures(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Game *p_game);

#endif
