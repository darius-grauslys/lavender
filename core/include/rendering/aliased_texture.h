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
void give_texture_to__aliased_texture(
        Aliased_Texture *p_aliased_texture,
        Texture *p_texture) {
#ifndef NDEBUG
    if (!p_aliased_texture) {
        debug_error("give_PLATFORM_texture_to__aliased_texture, p_aliased_texture == 0.");
        return;
    }
#endif
    p_aliased_texture->texture=
        *p_texture;
}

static inline
Texture get_texture_from__aliased_texture(
        Aliased_Texture *p_aliased_texture) {
#ifndef NDEBUG
    if (!p_aliased_texture) {
        debug_error("give_PLATFORM_texture_to__aliased_texture, p_aliased_texture == 0.");
        return (Texture){0};
    }
#endif
    return p_aliased_texture->texture;
}

static inline
bool is_aliased_texture__used(
        Aliased_Texture *p_aliased_texture) {
    return (bool)(p_aliased_texture && p_aliased_texture->name_of__texture__c_str[0]);
}

#endif
