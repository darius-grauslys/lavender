# Introduction

This tutorial shows how to expand the barebones stock scene__main.c
to also allocate and poll a world for allocation.

### Note - Extra Steps:
We do some extra steps beyond what is required to simply allocate
the world. This is to show the world allocation and polling to actually
work and generate a world.

# Build

Build the example with the following command:
`
lav_build -e PLATFORM=nogui FLAGS="-ggdb -w" -j$(nproc)
`

## Agent Advisory:

AI Agents should be aware that the outputted executable will NOT terminate
and should be ran with a timeout. To verify the example, it is sufficent to
read stdout, and verify that the transition was made.

## 1) Registering The Tileset Texture

We need to load the tileset texture in our m_load_scene_as__main_handler
like so:
`
register_aliased_textures(
        get_p_aliased_texture_manager_from__gfx_context(
            get_p_gfx_context_from__game(p_game)), 
        p_game);
`

Be sure to see source/rendering/implemented/aliased_texture_registrar.c
on how the textures are actually loaded. This loading behavior is not
apart of the default implemented/ stock .c files.

### Note - Consistency:
When loading resources for a scene they should be done in
`m_load_scene_as__[name of scene]_handler`

Those same resources should be release in:
`m_unload_scene_as__[name of scene]_handler`

## 2) Updating the Tile_Kind enum.

We are defining two tiles: RED and GREEN, they need to be added to
the Tile_Kind enum. Note the values of this enum must match 1:1 with
the tile index in the tile sheet.

The top left tile is index 0, and index increments left to right
and from top to bottom.

### Note - Include Shadowing
If you are not familiar with Lavender's usage of "Include Shadowing"
be sure to read ./examples/README.md
