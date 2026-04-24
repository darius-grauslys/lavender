# Overview

Tool scripts run relative to the directory that it is called from. 

The intended use of the script is to be called from a Lavender project, which will have ./include and ./source directories at the root of the project. 

The ./include and ./source directories are initially populated with all `*implemented*` wild character matching sub directories, with the parent 
directories recursively copied. So, from the game engine, core/include/types/implemented -> ./include/types/implemented to the project directory

# 1. File Existence Assumption

Assume all files within `*/implemented/*` exist and that
they are populated as the are found in ./core/

# 2. GEN- Fields

All code generation (unless explicitly prompted) will occur between
comment delimited GEN- fields.

# 3. --name Argument

If the script request mentions a --name argument, the argument must be
verified in the script as so:
First character is [a-zA-Z]
Remaining characters are alphanumeric and/or underscores.

# 4. [NAME]\_kind.h Files

A [NAME_OF_KIND_FILE]\_kind.h file usually follows the given pattern:

typedef enum [NAME_OF_KIND_FILE]\_Kind {
    [NAME_OF_KIND_FILE]\_Kind__None = 0,
    // GEN-BEGIN
    // GEN-END
    [NAME_OF_KIND_FILE]\_Kind__Unknown
} [NAME_OF_KIND_FILE]\_Kind;

Whenever a script request asks to update the [NAME_OF_KIND_FILE]\_kind.h 
file, use the --name argument to implement the script such that if:
[NAME_OF_KIND_FILE]\_Kind\_\_[--name]

# 5. Project Assets Directory

./assets
./assets/audio
./assets/disk
./assets/disk/worlds
./assets/entities
./assets/entities/entities__8x8
./assets/entities/entities__16x16
./assets/entities/entities__32x32
./assets/entities/entities__64x64
./assets/ui
./assets/ui/default
./assets/ui/default/\_ui_tileset_default.png
./assets/ui/default/\_ui_map\_\*.png
./assets/ui/font
./assets/ui/font/ui_tileset_font.png
./assets/ui/log
./assets/ui/sprites
./assets/ui/sprites/ui_sprite__8x8
./assets/ui/sprites/ui_sprite__16x16
./assets/ui/sprites/ui_sprite__32x32
./assets/ui/sprites/ui_sprite__8x8/\*.png
./assets/ui/sprites/ui_sprite__16x16/\*.png
./assets/ui/sprites/ui_sprite__32x32/\*.png
./assets/ui/typer
./assets/ui/xml
./assets/ui/xml/[PLATFORM]/[DIRS..]/\*.xml
./assets/world

## 5.1 ./assets/ui/default/\_ui_tileset_default.png
This file is the default tileset used.

At this time, there is only the default tileset.

## 5.2 ./assets/ui/default/\_ui_map\_\*.png
These .png files represent constructed maps from the default tileset.

## 5.3 ./assets/ui/sprites/ui_sprite__NxN/\*.png
These .png files are sprites composed of NxN pixel tiles.

## 5.4 ./assets/ui/xml/[PLATFORM]/[DIRS..]/\*.xml
These are the xml files which detail the structure
of UI elements on a ui_map.png file.
