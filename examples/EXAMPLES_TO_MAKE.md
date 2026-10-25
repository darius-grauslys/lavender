# Topics:

Legend: [done] = has an example under examples/ ; [partial] = covered
in passing, deserves its own example.

## Next up (in suggested order)
1. `types/01__tile_layer_resolutions` — Game Specific Config 2.2 (default
   logical tile layer resolutions) + 2.3 (bitfield size of tile layers).
   Scaffold from `types/00__tile_layers`.
2. `config/00__engine_config` — Game Specific Config 3 + 3.1 (engine macros
   in config/implemented/engine_config.h and optimizing them).
3. Audio registration (section below is empty — pick the first audio topic).

All examples in the Scene, Chunk Generation, and Entity sections are done.
Every example must: build clean, run with no `debug_error` spam, verify its
behavior (screenshot pixel analysis for SDL / stdout for no_gui), keep its
README in sync, and leave no build artifacts staged (see AGENTS.md §8).

## Scene registration and common setups:
1) how to register a scene [done: scene/00__empty_scene]
1.1) the scene_registrar [done]
1.2) updating Scene_Kind in types/implemented/scene [done]

2) how to setup a blank scene, explain what is happening [done: scene/00__empty_scene]

3) how to allocate a world and route chunk generator registration (suggest seeing chunk generator guide) [done: scene/01__allocate_world]

4) how to allocate graphics windows for the world [done: scene/01__allocate_world, scene/02__allocate_ui]
4.1) how by making a parent hierarchy of multiple windows we can support multiple layers in a tile_render_kernel [done: types/00__tile_layers]

5) how to allocate graphics windows for UI [done: scene/02__allocate_ui]

## Game Specific Configuration:
1) fundamentally explain how every file in core/ with "/implemented/" in its path is to be "Include Shadowed"
during the build process. In otherwords, its definitions therein are to replace whatever definitions the base
engine provides. [done: examples/README.md (root)]

2) Show how to accomplish various configurations in types/
2.1) changing the quantity of tile layers [done: types/00__tile_layers]
2.2) changing the default logical tile layer resolutions
2.3) changing the bitfield size of tile layers
2.4) defining the actual tile layers in the tile struct [done: types/00__tile_layers]

3) Show how most engine macros are found in config/implemented/engine_config.h
3.1) Show how to optimize the macros for various aspects of the engine

## Controling Chunk Generation
1) Show how to register a chunk generator [done: world/00__chunk_generator]
2) Show how to modify the tile_render_kernel [done: world/01__render_kernel]
2.1) Point to scene guides on how to configure the graphics windows for world render layering. [done: world/01__render_kernel README -> types/00__tile_layers]

## Entity registration
1) how to spawn and register an entity with a sprite and a client hitbox (tile logic ground, lazy sprite allocation, spawn-before-load ordering) [done: entity/00__spawn_entity]

## Audio registration

