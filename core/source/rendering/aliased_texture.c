#include "rendering/aliased_texture.h"
#include "defines.h"
#include "rendering/texture.h"
#include "serialization/serialization_header.h"

void initialize_aliased_texture(
        Aliased_Texture *p_aliased_texture) {
    initialize_texture(
            p_aliased_texture->texture);
    memset(p_aliased_texture
            ->name_of__texture__c_str,
            0,
            sizeof(p_aliased_texture->name_of__texture__c_str));
    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header*)p_aliased_texture, 
            sizeof(Aliased_Texture));
}

void set_c_str_of__aliased_texture(
        Aliased_Texture *p_aliased_texture,
        const char *c_str) {
    Quantity__u32 length_of__c_str =
        strnlen(c_str, MAX_LENGTH_OF__TEXTURE_NAME);
    memcpy(p_aliased_texture
            ->name_of__texture__c_str,
            c_str,
            length_of__c_str);
}

bool is_c_str_matching__aliased_texture(
        Aliased_Texture *p_aliased_texture,
        const char *c_str) {
    for (Index__u32 index_of__c_str = 0;
            index_of__c_str
            < MAX_LENGTH_OF__TEXTURE_NAME;
            index_of__c_str++) {
        if (!c_str[index_of__c_str])
            break;
        if (c_str[index_of__c_str]
                != p_aliased_texture
                ->name_of__texture__c_str[index_of__c_str]) {
            return false;
        }
    }
    return true;
}
