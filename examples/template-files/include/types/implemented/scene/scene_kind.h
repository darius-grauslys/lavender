#ifndef IMPL_SCENE_KIND_H
#define IMPL_SCENE_KIND_H

#define DEFINE_SCENE_KIND

typedef enum Scene_Kind {
    Scene_Kind__None = 0,
    // GEN-BEGIN
    Scene_Kind__Main_Menu = Scene_Kind__None,
    Scene_Kind__Main_Menu__Singleplayer,
    Scene_Kind__Main_Menu__Multiplayer,
    Scene_Kind__Main_Menu__Settings,
    Scene_Kind__World__Overworld,
    Scene_Kind__World__Underworld,
    Scene_Kind__World__Aether,
    // GEN-END
    Scene_Kind__Unknown
} Scene_Kind;

#endif
