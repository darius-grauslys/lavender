#include "rendering/aliased_texture_manager.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "platform_defines.h"
#include "random.h"
#include "rendering/aliased_texture.h"
#include "defines.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"

static inline
Aliased_Texture *get_p_aliased_texture_by__index_from__aliased_texture_manager(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Index__u32 index_of__aliased_texture) {
    if (MAX_QUANTITY_OF__ALIASED_TEXTURES
            <= index_of__aliased_texture) {
        debug_error("get_p_aliased_texture_by__index_from__aliased_texture_manager, index out of bounds: %d/%d", index_of__aliased_texture, MAX_QUANTITY_OF__ALIASED_TEXTURES);
        return 0;
    }
    return &p_aliased_texture_manager
        ->aliased_textures[index_of__aliased_texture];
}

void initialize_aliased_texture_manager(
        Aliased_Texture_Manager *p_aliased_texture_manager) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_aliased_texture_manager
                ->aliased_textures, 
            MAX_QUANTITY_OF__ALIASED_TEXTURES, 
            sizeof(Aliased_Texture));
    initialize_repeatable_psuedo_random(
            &p_aliased_texture_manager
            ->repeatable_psuedo_random_for__texture_uuid, 
            (uint32_t)(uint64_t)p_aliased_texture_manager);
}

Aliased_Texture *get_p_aliased_texture_thats__available_from__manager(
        Aliased_Texture_Manager *p_aliased_texture_manager) {
    Aliased_Texture *p_aliased_texture__available = 0;
    for (Index__u32 index_of__aliased_texture = 0;
            index_of__aliased_texture
            < MAX_QUANTITY_OF__ALIASED_TEXTURES;
            index_of__aliased_texture++) {
        Aliased_Texture *p_aliased_texture =
            get_p_aliased_texture_by__index_from__aliased_texture_manager(
                    p_aliased_texture_manager, 
                    index_of__aliased_texture);
        if (is_aliased_texture__used(p_aliased_texture)) {
            continue;
        }
        p_aliased_texture__available = 
            p_aliased_texture;
        break;
    }

    return p_aliased_texture__available;
}

///
/// WARNING: You do not own the returned texture.
///
bool allocate_texture_with__alias(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str,
        Texture_Flags texture_flags,
        Texture *p_OUT_texture) {
    Texture __tmp_texture;
    if (!p_OUT_texture)
        p_OUT_texture = &__tmp_texture;
    if (!name_of__texture__c_str[0]) {
        debug_error("allocate_texture_with__alias, alias cannot be empty.");
        return 0;
    }

    Aliased_Texture *p_aliased_texture__available =
        (Aliased_Texture*)allocate_serialization_header_with__uuid_branding(
                (Serialization_Header*)p_aliased_texture_manager->aliased_textures, 
                MAX_QUANTITY_OF__ALIASED_TEXTURES, 
                &p_aliased_texture_manager->repeatable_psuedo_random_for__texture_uuid, 
                GET_UUID_BRANDING(
                    Lavender_Type__Aliased_Texture,
                    0));
    if (!p_aliased_texture__available) {
        debug_error("allocate_texture_with__alias, too many aliased textures are allocated.");
        return true;
    }

    if (PLATFORM_allocate_texture(
                p_PLATFORM_gfx_context, 
                p_PLATFORM_gfx_window,
                texture_flags,
                p_OUT_texture)) {
        debug_error("allocate_texture_with__alias, failed to allocate texture.");
        return true;
    }

    set_c_str_of__aliased_texture(
            p_aliased_texture__available, 
            name_of__texture__c_str);
    give_texture_to__aliased_texture(
            p_aliased_texture__available, 
            p_OUT_texture);
    initialize_serialization_header(
            (Serialization_Header*)p_aliased_texture__available, 
            get_next_available__random_uuid_in__contiguous_array(
                (Serialization_Header*)p_aliased_texture_manager
                ->aliased_textures, 
                MAX_QUANTITY_OF__ALIASED_TEXTURES, 
                &p_aliased_texture_manager
                    ->repeatable_psuedo_random_for__texture_uuid), 
            sizeof(Aliased_Texture));
    return false;
}

bool load_texture_from__path_with__alias(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str,
        Texture_Flags texture_flags,
        const char *c_str__path,
        Texture *p_OUT_texture) {
    Texture __tmp_texture;
    if (!p_OUT_texture)
        p_OUT_texture = &__tmp_texture;
    if (!name_of__texture__c_str[0]) {
        debug_error("load_texture_from__path_with__alias, alias cannot be empty.");
        return true;
    }

    Aliased_Texture *p_aliased_texture__available =
        (Aliased_Texture*)allocate_serialization_header_with__uuid_branding(
                (Serialization_Header*)p_aliased_texture_manager->aliased_textures, 
                MAX_QUANTITY_OF__ALIASED_TEXTURES, 
                &p_aliased_texture_manager->repeatable_psuedo_random_for__texture_uuid, 
                GET_UUID_BRANDING(
                    Lavender_Type__Aliased_Texture,
                    0));
    if (!p_aliased_texture__available) {
        debug_error("load_texture_from__path_with__alias, too many aliased textures are allocated.");
        return true;
    }

    IO_path full_path;
    memset(full_path,
            0,
            sizeof(full_path));
    Quantity__u32 length_of__base_directory = 
        PLATFORM_get_base_directory(full_path);
    if (MAX_LENGTH_OF__IO_PATH 
            <= length_of__base_directory) {
        debug_error("load_texture_from__path_with__alias, game directory exceeds MAX_LENGTH_OF__IO_PATH.");
        return true;
    }
    full_path[length_of__base_directory++] = '/';
    memcpy(&full_path[length_of__base_directory],
            c_str__path,
            MAX_LENGTH_OF__IO_PATH
            - length_of__base_directory);

    if (PLATFORM_allocate_texture_with__path(
                p_PLATFORM_gfx_context,
                p_PLATFORM_gfx_window,
                texture_flags,
                full_path,
                p_OUT_texture)) {
        debug_error("load_texture_from__path_with__alias, failed to allocate texture.");
        return true;
    }

    set_c_str_of__aliased_texture(
            p_aliased_texture__available, 
            name_of__texture__c_str);
    give_texture_to__aliased_texture(
            p_aliased_texture__available, 
            p_OUT_texture);
    return false;
}

static inline
Aliased_Texture *get_p_aliased_texture_by__alias(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str) {
    Aliased_Texture *p_aliased_texture__matching = 0;
    for (Index__u32 index_of__aliased_texture = 0;
            index_of__aliased_texture
            < MAX_QUANTITY_OF__ALIASED_TEXTURES;
            index_of__aliased_texture++) {
        Aliased_Texture *p_aliased_texture =
            get_p_aliased_texture_by__index_from__aliased_texture_manager(
                    p_aliased_texture_manager, 
                    index_of__aliased_texture);
        if (!is_aliased_texture__used(p_aliased_texture)) {
            continue;
        }
        if (is_c_str_matching__aliased_texture(
                    p_aliased_texture, 
                    name_of__texture__c_str)) {
            p_aliased_texture__matching = 
                p_aliased_texture;
            break;
        }
    }
    if (!p_aliased_texture__matching) {
        return 0;
    }

    return p_aliased_texture__matching;
}

Identifier__u32 get_uuid_of__aliased_texture(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str) {
    Aliased_Texture *p_aliased_texture__matching =
        get_p_aliased_texture_by__alias(
                p_aliased_texture_manager, 
                name_of__texture__c_str);

    if (!p_aliased_texture__matching) {
        char name_of__texture__copied__c_str[MAX_LENGTH_OF__TEXTURE_NAME+1];
        memcpy(
                name_of__texture__copied__c_str,
                name_of__texture__c_str,
                MAX_LENGTH_OF__TEXTURE_NAME);
        name_of__texture__copied__c_str[MAX_LENGTH_OF__TEXTURE_NAME] = 0;
        debug_error("get_uuid_of__aliased_texture, failed to find texture for given name: %s", name_of__texture__copied__c_str);
    }

    return GET_UUID_P(p_aliased_texture__matching);
}

bool get_texture_by__alias(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str,
        Texture *p_OUT_texture) {
    Aliased_Texture *p_aliased_texture__matching =
        get_p_aliased_texture_by__alias(
                p_aliased_texture_manager, 
                name_of__texture__c_str);

    if (!p_aliased_texture__matching) {
        char name_of__texture__copied__c_str[MAX_LENGTH_OF__TEXTURE_NAME+1];
        memcpy(
                name_of__texture__copied__c_str,
                name_of__texture__c_str,
                MAX_LENGTH_OF__TEXTURE_NAME);
        name_of__texture__copied__c_str[MAX_LENGTH_OF__TEXTURE_NAME] = 0;
        debug_error("get_texture_by__alias, failed to find texture for given name: %s", name_of__texture__copied__c_str);
        return true;
    }

    *p_OUT_texture = get_texture_from__aliased_texture(
            p_aliased_texture__matching);
    return false;
}

static inline
Aliased_Texture *get_p_aliased_texture_by__uuid(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Identifier__u32 uuid__u32) {
    Aliased_Texture *p_aliased_texture =
        (Aliased_Texture*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)p_aliased_texture_manager
                ->aliased_textures, 
                MAX_QUANTITY_OF__ALIASED_TEXTURES, 
                uuid__u32);

    return p_aliased_texture;
}

bool get_texture_by__uuid(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Identifier__u32 uuid__u32,
        Texture *p_OUT_texture) {
    Aliased_Texture *p_aliased_texture =
        get_p_aliased_texture_by__uuid(
                p_aliased_texture_manager, 
                uuid__u32);

    if (!p_aliased_texture) {
        debug_error("get_texture_by__uuid, failed to find texture.");
        return true;
    }

    *p_OUT_texture =
        get_texture_from__aliased_texture(
            p_aliased_texture);
    return false;
}

void release_all_aliased_textures(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Aliased_Texture_Manager *p_aliased_texture_manager) {
    for (Index__u32 index_of__aliased_texture = 0;
            index_of__aliased_texture
            < MAX_QUANTITY_OF__ALIASED_TEXTURES;
            index_of__aliased_texture++) {
        Aliased_Texture *p_aliased_texture =
            get_p_aliased_texture_by__index_from__aliased_texture_manager(
                    p_aliased_texture_manager, 
                    index_of__aliased_texture);
        PLATFORM_release_texture(
                p_PLATFORM_gfx_context, 
                p_aliased_texture->texture);
        initialize_aliased_texture(p_aliased_texture);
    }
}

void release_aliased_texture_by__uuid(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Identifier__u32 uuid__u32) {
    Aliased_Texture *p_aliased_texture =
        get_p_aliased_texture_by__uuid(
                p_aliased_texture_manager, 
                uuid__u32);

    if (!p_aliased_texture) {
        debug_warning("release_aliased_texture_by__uuid, failed to find.");
        return;
    }

    PLATFORM_release_texture(
            p_PLATFORM_gfx_context, 
            p_aliased_texture->texture);
    initialize_aliased_texture(p_aliased_texture);
}

void release_aliased_texture_by__alias(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str) {
    Aliased_Texture *p_aliased_texture =
        get_p_aliased_texture_by__alias(
                p_aliased_texture_manager, 
                name_of__texture__c_str);

    if (!p_aliased_texture) {
        debug_warning("release_aliased_texture_by__alias, failed to find.");
        return;
    }

    PLATFORM_release_texture(
            p_PLATFORM_gfx_context, 
            p_aliased_texture->texture);
    initialize_aliased_texture(p_aliased_texture);
}
