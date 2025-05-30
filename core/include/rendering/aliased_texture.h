#ifndef ALIASED_TEXTURE_H
#define ALIASED_TEXTURE_H

#include "defines.h"

///
/// Double calling this will leak memory.
///
void initialize_aliased_texture(
        Aliased_Texture *p_aliased_texture);

void set_c_str_of__aliased_texture(
        Aliased_Texture *p_aliased_texture,
        const char *c_str);

bool is_c_str_matching__aliased_texture(
        Aliased_Texture *p_aliased_texture,
        const char *c_str);

static inline
void give_PLATFORM_texture_to__aliased_texture(
        Aliased_Texture *p_aliased_texture,
        PLATFORM_Texture *P_PLATFORM_texture) {
#ifndef NDEBUG
    if (!p_aliased_texture) {
        debug_error("give_PLATFORM_texture_to__aliased_texture, p_aliased_texture == 0.");
        return;
    }
#endif
    p_aliased_texture->P_PLATFORM_texture =
        P_PLATFORM_texture;
}

static inline
PLATFORM_Texture *get_p_PLATFORM_texture_from__aliased_texture(
        Aliased_Texture *p_aliased_texture) {
#ifndef NDEBUG
    if (!p_aliased_texture) {
        debug_error("give_PLATFORM_texture_to__aliased_texture, p_aliased_texture == 0.");
        return 0;
    }
#endif
    return p_aliased_texture->P_PLATFORM_texture;
}

static inline
bool is_aliased_texture__used(
        Aliased_Texture *p_aliased_texture) {
    return (bool)(p_aliased_texture && p_aliased_texture->name_of__texture__c_str[0]);
}

#endif
