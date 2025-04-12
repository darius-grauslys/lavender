#include "rendering/implemented/sprite_gfx_allocator_registrar.h"

void register_sprite_gfx_allocators(
        Sprite_Gfx_Allocation_Manager *p_sprite_gfx_allocator_manager) {
    debug_warning("impl, register_sprite_gfx_allocators");

// Register with:
    // register_sprite_gfx_allocator_for__entity(
    //     Sprite_Gfx_Allocation_Manager *p_sprite_gfx_allocator_manager,
    //     Entity_Kind the_kind_of__entity,
    //     f_Sprite_Gfx_Allocator f_sprite_gfx_allocator) {

    // register_sprite_gfx_allocator_for__ui(
    //     Sprite_Gfx_Allocation_Manager *p_sprite_gfx_allocator_manager,
    //     UI_Sprite_Kind the_kind_of__ui,
    //     f_Sprite_Gfx_Allocator f_sprite_gfx_allocator);

    // register_sprite_gfx_allocator_for__item(
    //         Sprite_Gfx_Allocation_Manager *p_sprite_gfx_allocator_manager,
    //         Item_Kind the_kind_of__item,
    //         f_Sprite_Gfx_Allocator f_sprite_gfx_allocator);

// Allocate with:
    // allocate_sprite__entity(
    //     Gfx_Context *p_gfx_context,
    //     Graphics_Window *p_gfx_window,
    //     Sprite_Gfx_Allocation_Manager *p_sprite_gfx_allocator_manager,
    //     Sprite_Wrapper *p_sprite_wrapper,
    //     Entity_Kind the_kind_of__entity);

    // allocate_sprite__ui(
    //     Gfx_Context *p_gfx_context,
    //     Graphics_Window *p_gfx_window,
    //     Sprite_Gfx_Allocation_Manager *p_sprite_gfx_allocator_manager,
    //     Sprite_Wrapper *p_sprite_wrapper,
    //     UI_Sprite_Kind the_kind_of__ui);

    // allocate_sprite__item(
    //     Gfx_Context *p_gfx_context,
    //     Graphics_Window *p_gfx_window,
    //     Sprite_Gfx_Allocation_Manager *p_sprite_gfx_allocator_manager,
    //     Sprite_Wrapper *p_sprite_wrapper,
    //     Item_Kind the_kind_of__item) {
}
