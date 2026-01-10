#include "rendering/sprite_pool.h"
#include "collisions/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "platform_defines.h"
#include "rendering/gfx_context.h"
#include "rendering/sprite.h"
#include "rendering/texture.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "sort/heap_sort__opaque.h"
#include "types/implemented/sprite_animation_kind.h"

void initialize_sprite_pool(
        Sprite_Pool *p_sprite_pool) {
#ifndef NDEBUG
    if (!p_sprite_pool) {
        debug_error("initialize_sprite_pool, p_sprite_pool == 0.");
        return;
    }
#endif
    memset(p_sprite_pool,
            0,
            sizeof(Sprite_Pool));
    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header *)p_sprite_pool, 
            sizeof(Sprite_Pool));
}

bool allocate_sprite_pool__members(
        Sprite_Pool *p_sprite_pool,
        Quantity__u32 quantity_of__sprites__u32) {
    initialize_sprite_pool(p_sprite_pool);

    p_sprite_pool->pM_pool_of__sprites = malloc(sizeof(Sprite) * quantity_of__sprites__u32);

    if (!p_sprite_pool->pM_pool_of__sprites) {
        debug_error("allocate_sprite_pool__members, failed to dynamically allocate sprite data (malloc == 0.)");
        return false;
    }

    p_sprite_pool->pM_sprite_render_records = malloc(sizeof(Sprite_Render_Record) * quantity_of__sprites__u32);

    if (!p_sprite_pool->pM_sprite_render_records) {
        free(p_sprite_pool->pM_pool_of__sprites);
        debug_error("allocate_sprite_pool__members, failed to dynamically allocate sprite render data (malloc == 0.)");
        return false;
    }

    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_sprite_pool->pM_pool_of__sprites,
            quantity_of__sprites__u32, 
            sizeof(Sprite));
    p_sprite_pool->p_sprite_render_record__last =
        p_sprite_pool->pM_sprite_render_records;
    memset(
            p_sprite_pool->pM_sprite_render_records, 
            0, 
            sizeof(Sprite_Render_Record) * quantity_of__sprites__u32);

    return true;
}

Sprite *allocate_sprite_from__sprite_pool(
        Gfx_Context *p_gfx_context,
        Sprite_Pool *p_sprite_pool,
        Graphics_Window *p_gfx_window,
        Identifier__u32 uuid__u32,
        Texture texture_to__sample_by__sprite,
        Texture_Flags texture_flags_for__sprite) {
#ifndef NDEBUG
    if (!p_sprite_pool) {
        debug_error("allocate_sprite_from__sprite_pool, p_sprite_pool == 0.");
        return 0;
    }
    if (is_identifier_u32__invalid(uuid__u32)) {
        debug_error("allocate_sprite_from__sprite_pool, uuid__u32 is invalid.");
        return 0;
    }
#endif
    Sprite *p_sprite =
        (Sprite*)get_next_available__allocation_in__contiguous_array(
                (Serialization_Header*)p_sprite_pool->pM_pool_of__sprites, 
                MAX_QUANTITY_OF__SPRITES, 
                uuid__u32);

    if (!p_sprite) {
        debug_error("allocate_sprite_from__sprite_pool, failed to allocate sprite.");
        return 0;
    }

    p_sprite->texture_for__sprite_to__sample =
        texture_to__sample_by__sprite;

    if (PLATFORM_allocate_texture(
                get_p_PLATFORM_gfx_context_from__gfx_context(
                    p_gfx_context), 
                p_gfx_window->p_PLATFORM_gfx_window,
                texture_flags_for__sprite,
                &p_sprite->texture_of__sprite)) {
        debug_error("allocate_sprite_from__sprite_pool, failed to allocate p_PLATFORM_texture_of__sprite.");
        PLATFORM_release_sprite(
                p_gfx_context, 
                p_sprite->p_PLATFORM_sprite);
        DEALLOCATE_P(p_sprite);
        return 0;
    }

    PLATFORM_Sprite *p_PLATFORM_sprite =
        PLATFORM_allocate_sprite(
                p_gfx_context,
                p_gfx_window,
                p_sprite,
                texture_flags_for__sprite);

    if (!p_PLATFORM_sprite) {
        debug_error("allocate_sprite_from__sprite_pool, failed to allocate p_PLATOFRM_sprite.");
        PLATFORM_release_texture(
                get_p_PLATFORM_gfx_context_from__gfx_context(
                    p_gfx_context), 
                p_sprite->texture_of__sprite);
        DEALLOCATE_P(p_sprite);
        return 0;
    }

    ALLOCATE_P(p_sprite, uuid__u32);

    p_sprite->p_PLATFORM_sprite =
        p_PLATFORM_sprite;

    p_sprite_pool
        ->p_sprite_render_record__last
        ->p_sprite = p_sprite;
    p_sprite_pool->p_sprite_render_record__last++;

    set_sprite_as__enabled(p_sprite);

    return p_sprite;
}

void release_sprite_from__sprite_pool(
        Gfx_Context *p_gfx_context,
        Sprite_Pool *p_sprite_pool,
        Sprite *p_sprite) {
#ifndef NDEBUG
    if (!p_sprite_pool) {
        debug_error("release_sprite_from__sprite_pool, p_sprite_pool == 0.");
        return;
    }
    if (!p_sprite) {
        debug_error("release_sprite_from__sprite_pool, p_sprite == 0.");
        return;
    }
    if (p_sprite - p_sprite_pool->pM_pool_of__sprites 
            >= p_sprite_pool->max_quantity_of__sprites) {
        debug_error("release_sprite_from__sprite_pool, p_sprite is not allocated with this manager.");
        return;
    }
#endif

    if (p_sprite->p_PLATFORM_sprite) {
        PLATFORM_release_sprite(
                p_gfx_context, 
                p_sprite->p_PLATFORM_sprite);
    }

    Sprite_Render_Record *p_sprite_render_record =
        p_sprite_pool->pM_sprite_render_records;

    do {
        if (p_sprite_render_record->p_sprite
                == p_sprite) {
            break;
        }
    } while ((++p_sprite_render_record)->p_sprite
            && p_sprite_render_record 
            < p_sprite_pool->p_sprite_render_record__last);

    p_sprite_pool->p_sprite_render_record__last--;
    *p_sprite_render_record =
        *p_sprite_pool->p_sprite_render_record__last;
    p_sprite_pool
        ->p_sprite_render_record__last
        ->p_sprite = 0;

    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header*)p_sprite, 
            sizeof(Sprite));
}

static Signed_Quantity__i32 f_sort_heuristic__sprite_render_record(
        void *p_context,
        void *pv_sprite_render_record__one,
        void *pv_sprite_render_record__two) {
    Sprite_Render_Record *p_sprite_render_record__one = 
        (Sprite_Render_Record*)pv_sprite_render_record__one;
    Sprite_Render_Record *p_sprite_render_record__two = 
        (Sprite_Render_Record*)pv_sprite_render_record__two;

    if (p_sprite_render_record__one
            ->position__3i32F4
            .z__i32F4 >
            p_sprite_render_record__two
            ->position__3i32F4
            .z__i32F4) {
        return 1;
    }

    if (p_sprite_render_record__one
            ->position__3i32F4
            .y__i32F4 <
            p_sprite_render_record__two
            ->position__3i32F4
            .y__i32F4) {
        return 1;
    }

    return -1;
}

void f_sort_swap__sprite_render_record(
        void *p_context,
        void *pv_sprite_render_record__one,
        void *pv_sprite_render_record__two) {
    Sprite_Render_Record *p_sprite_render_record__one = 
        (Sprite_Render_Record*)pv_sprite_render_record__one;
    Sprite_Render_Record *p_sprite_render_record__two = 
        (Sprite_Render_Record*)pv_sprite_render_record__two;

    Sprite_Render_Record temporary =
        *p_sprite_render_record__one;

    *p_sprite_render_record__one =
        *p_sprite_render_record__two;

    *p_sprite_render_record__two =
        temporary;
}

void render_sprites_in__sprite_pool(
        Game *p_game,
        Sprite_Manager *p_sprite_manager,
        Sprite_Pool *p_sprite_pool,
        Graphics_Window *p_gfx_window) {
    Sprite_Render_Record *p_sprite_render_record = 
        p_sprite_pool->pM_sprite_render_records;

    if (!p_sprite_render_record->p_sprite)
        return;

    do {
        if (!is_sprite__enabled(
                    p_sprite_render_record
                    ->p_sprite)) {
            continue;
        }
        poll_sprite_for__animation(
                p_game,
                p_sprite_render_record->p_sprite,
                p_sprite_manager);
        Hitbox_AABB *p_hitbox_aabb =
            get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                    get_p_hitbox_aabb_manager_from__game(p_game), 
                    GET_UUID_P(p_sprite_render_record
                        ->p_sprite));
        if (!p_hitbox_aabb) {
            debug_warning("render_sprites_in__sprite_pool, p_sprite lacks hitbox component.");
            set_sprite_as__disabled(
                    p_sprite_render_record
                    ->p_sprite);
            continue;
        }
        p_sprite_render_record->position__3i32F4 =
            p_hitbox_aabb->position__3i32F4;
        p_sprite_render_record->position__3i32F4.x__i32F4 -=
            i32_to__i32F4(
                    get_length_of__texture_flag__width(
                        p_sprite_render_record
                        ->p_sprite
                        ->texture_of__sprite
                        .texture_flags)) >> 2; // TODO: why >> 2 and not >> 1?
    } while ((++p_sprite_render_record)->p_sprite
            && p_sprite_render_record 
            < p_sprite_pool->p_sprite_render_record__last);

    heap_sort__opaque(
            p_game,
            p_sprite_pool->pM_sprite_render_records, 
            p_sprite_pool->p_sprite_render_record__last
            - p_sprite_pool->pM_sprite_render_records, 
            sizeof(Sprite_Render_Record),
            f_sort_heuristic__sprite_render_record,
            f_sort_swap__sprite_render_record);

    p_sprite_render_record = 
        p_sprite_pool->pM_sprite_render_records;

    do {
        if (!is_sprite__enabled(
                    p_sprite_render_record
                    ->p_sprite)) {
            continue;
        }
        PLATFORM_render_sprite(
                get_p_gfx_context_from__game(p_game), 
                p_gfx_window, 
                p_sprite_render_record->p_sprite, 
                p_sprite_render_record->position__3i32F4);
    } while ((++p_sprite_render_record)->p_sprite
            && p_sprite_render_record 
            < p_sprite_pool->p_sprite_render_record__last);
}

Sprite *get_p_sprite_by__uuid_from__sprite_pool(
        Sprite_Pool *p_sprite_pool,
        Identifier__u32 uuid__u32) {
#ifndef NDEBUG
    if (!p_sprite_pool) {
        debug_error("get_p_sprite_by__uuid_from__sprite_pool, p_sprite_pool == 0.");
        return 0;
    }
#endif

    Sprite *p_sprite =
        (Sprite*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)p_sprite_pool->pM_pool_of__sprites, 
                MAX_QUANTITY_OF__SPRITES, 
                uuid__u32);

    return p_sprite;
}
