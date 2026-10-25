# Introduction

The default scene__main.c which ships from the base 
source/scene/implemented/scene__main.c already shows how a barebones scene is
made and registered.

Therefore this guide will explain the structure and extension process of
adding additional scenes, as well as transitioning between scenes.

# Build

Build the example with the following command:
`
lav_build -e PLATFORM=nogui FLAGS="-ggdb -w" -j$(nproc)
`

# Scene Driver

Scenes are driven in:
$LAVENDER_DIR/core/source/game.c, `run_game(Game *p_game)`

## 1) Entry

In ./include/types/implemented/scene/scene_kind.h, we specify the default entry
scene like so:

`
Scene_Kind__None = 0,
Scene_Kind__My_First_Scene = Scene_Kind__None,
`

Then in ./source/scene/implemented/scene_registrar.c we write:

`
register_scene__my_first_scene(p_scene_manager);
`

Finally in the actual scene .c file, lets say based on prior examples it's:
./source/scene/implemented/scene__my_first_scene.c

In the function register_scene__my_first_scene (which is near identical to stock
register_scene__main, from scene__main.c):

`
    register_scene_into__scene_manager(
            p_scene_manager, 
            Scene_Kind__My_First_Scene, 
            m_load_scene_as__main_handler, 
            m_enter_scene_as__main_handler, 
            m_unload_scene_as__main_handler);
`

## 2) Scene Traversal

Use the following function from scene_manager.h:
`set_active_scene_for__scene_manager(p_scene_manager, the_kind_of__scene)`

Practically, this is done line so:
`
set_active_scene_for__scene_manager(
        get_p_scene_manager_from__game(p_game),
        Scene_Kind__My_First_Scene);
`

This call can be made from any context where p_game is present.

The scene will NOT immediately transfer, instead the scene will
transfer after the current game tick completes.

### Game Tick Note:

A "game tick" is a single loop of the scene's poll, we can see this
in stock scene__main.c lines 22-34, a single while loop iteration is
a game tick.

## 3) Quit Scene State Machine

To quit scene management - and also quit the game - invoke the function:
`
quit_scene_state_machine(get_p_scene_manager_from__game(p_game));
`

This can be invoked in any context where p_game is present.
This will cause the game to exit on the next game tick.

### Note - Exit Hang:

If the game does not exit in a timely manner it may
be due to orphaned Serialization_Requests.
