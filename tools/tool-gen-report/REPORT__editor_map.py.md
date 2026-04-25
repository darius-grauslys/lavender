# editor_map.py Specification Review Report

Generated: 2026-04-25  
Revision: 4 (spec updated with engine source file references)

---

## BLOCKING Issues

### B-1: Section 1.1.4 "Container/Inventory Edit" is copy-pasted placeholder with no real spec

**Severity: BLOCKING (deferrable)**

Section 1.1.4.1.1 is titled "Tile Select" but says "THIS MODE IS PLACEHOLDER AT THIS TIME." Section 1.1.4.1.2 is titled "Entity Pan" (not "Inventory Pan"). The entire mode description is a skeleton with copy-paste artifacts from Entity Edit. There is no definition of valid selections, no inventory display spec, and no tool behavior.

**Recommendation:** Defer entirely. Implement a stub mode that displays "Not yet implemented" in the workspace. The spec itself acknowledges this is placeholder.

### B-2: Section 1.3 "Properties HUD" has no field definitions

**Severity: BLOCKING (soft — derivable from engine source)**

Section 1.3 only specifies anchoring/resizing behavior. It never defines what fields are shown for each object type, whether fields are editable or read-only, or how validated input fields (section 1.7) map to object properties.

Now that we have the engine source, we can derive the fields:

**For Global_Space** (from `defines.h`):
- `chunk_vector__3i32` (x, y, z) — read-only i32 × 3
- `quantity_of__references` — read-only u16
- `global_space_flags__u8` — read-only u8 bitfield

**For Tile** (from `defines.h` + project-local `tile.h`):
- Tile layer enum fields from `GEN-RENDER-BEGIN/END` block — editable enum dropdowns
- Raw byte view via `array_of__tile_data__u8[N]` — read-only hex display

**For Entity** (from `defines.h` + `entity_data.h`):
- `_serialization_header.uuid` — read-only u32
- `entity_data.entity_flags` — editable u32 bitfield
- `entity_data.the_kind_of__entity` — editable enum (Entity_Kind)

**Recommendation:** Accept the derived fields above as the initial implementation. Confirmation from spec author is desirable but not strictly required.

### B-3: C header parsing for project-local types is a significant unspecified feature

**Severity: BLOCKING (scoped and tractable)**

Section 4.5 says the editor must load types from `./include/types/implemented/*` (project-local). The editor needs to parse C headers to determine:
1. Enum values (e.g., `Tile_Kind`, `Entity_Kind`) — for dropdowns and tile palettes.
2. Struct layouts (e.g., `Tile`, `Entity_Data`) — for binary serialization.
3. Bitfield widths — for correct memory layout.

**For enums:** The `GEN-LOGIC-BEGIN` / `GEN-LOGIC-END` and `GEN-NO-LOGIC-BEGIN` / `GEN-NO-LOGIC-END` markers in `tile_kind.h` indicate code generation. The editor can parse between these markers. The example files (`examples/template-files/`) show the populated versions.

**For the Tile struct:** The template `tile.h` reveals the pattern. The `Tile` struct uses a union of bitfields with a `u8 array_of__tile_data__u8[N]` member that gives the exact byte size. The comment confirms: "3 is deterministically automatically generated via scripting." This means:
- The editor can extract `sizeof(Tile)` by parsing the array size from `array_of__tile_data__u8[N]`.
- The editor can extract tile layer enum fields from the `GEN-RENDER-BEGIN/END` block.
- The editor does NOT need full C struct/bitfield parsing.

**For Entity_Data:** The engine default (`entity_data.h`) has 2 fields: `entity_flags` (u32) + `the_kind_of__entity` (enum). Projects can override via `DEFINE_ENTITY_DATA`.

**Recommendation:** For the initial implementation:
1. **Enum parsing:** Implement a simple C enum parser that handles sequential values, explicit assignments, and `GEN-*` markers.
2. **Tile struct parsing:** Extract `sizeof(Tile)` from the `array_of__tile_data__u8[N]` pattern. Extract tile layer fields from `GEN-RENDER-BEGIN/END`.
3. **Entity_Data parsing:** Use the engine-default layout. Warn if the project overrides it with an unrecognized layout.

This is tractable. The blocking status is: **the enum parser and tile-size extractor must be implemented before tile editing or serialization can work.**

---

## RESOLVED Issues

### ~~Tile serialization format entirely unspecified~~

**RESOLVED.** The engine source files are now available. The `Chunk` struct layout is visible in `defines.h`. The filesystem layout is visible in `world_directory.c`.

### ~~No specification of Global_Space binary serialization format~~

**RESOLVED.** `global_space_manager.c` and `world_directory.c` are now available. The Global_Space is not directly serialized as a monolithic blob — instead, its components are serialized to separate files (`t`, `e`, `i`) within the chunk directory tree. The `Serialization_Header__UUID_64` provides the 64-bit UUID.

### ~~Chunk_Data layout needs clarification~~

**RESOLVED.** All chunk dimension constants are now known from `platform_defaults.h`. Tile indexing formula is confirmed from `chunk.h`. Template `tile.h` shows how `sizeof(Tile)` is deterministically encoded.

**Chunk dimensions (from `platform_defaults.h`):**
```
CHUNK__WIDTH  = BIT(3) = 8
CHUNK__HEIGHT = BIT(3) = 8   (NOTE: macro is `CHUNK_HEIGHT` — missing double underscore, typo in engine)
CHUNK__DEPTH  = BIT(1) = 2
CHUNK__QUANTITY_OF__TILES = 8 * 8 * 2 = 128
```

**Tile indexing within chunk (from `chunk.h`):**
```c
Index__u16 index = x + ((CHUNK__HEIGHT-1 - y) * CHUNK__WIDTH) + (CHUNK__WIDTH * CHUNK__HEIGHT * z);
```
**IMPORTANT:** Y-axis is inverted! `y=0` maps to the bottom row visually but the last row in memory.

**Filesystem layout (from `world_directory.c`):**
- `save/<world_name>/` — world root
- `save/<world_name>/h` — world header file
- `save/<world_name>/r_<hex8>_<hex8>_<hex8>/` — region directories
- Region dirs contain 6-level recursive quad-tree `c_<hex2>_<hex2>_<hex2>/` directories
- Leaf chunk directory: `c_<hex2>_<hex2>_<hex2>/`
- Chunk files: `t` (tiles), `e` (entities), `i` (inventories)

---

## NON-BLOCKING Issues (to revisit)

### NB-1: `editor_map.json` configuration file format is never defined

The spec references "configurable" properties and an `editor_map.json` in `./assets`, but never provides a schema or example.

**Impact:** Implementable with sensible defaults. Define a minimal schema:
```json
{
    "chunk_width": 8,
    "chunk_height": 8,
    "chunk_depth": 2,
    "engine_dir": ".",
    "project_dir": "."
}
```

### NB-2: Section 1.5.1 "Writing Messages to Message HUD" is empty

The section header exists but has no content. The existing `message_hud.py` in `tools/editor_ui_modules/` implements `INFO` and `ERROR` levels. The spec also mentions `SYSTEM` messages.

**Impact:** Add `SYSTEM` level to the existing `MsgLevel` enum. The existing `MessageHUD` class is a solid foundation.

### NB-3: Entity struct layout depends on project-local headers

`entity_data.h` in the engine defines:
```c
typedef struct Entity_Data_t {
    Entity_Flags__u32 entity_flags;
    Entity_Kind the_kind_of__entity;
} Entity_Data;
```

But the project can override this via `DEFINE_ENTITY_DATA`. The `Entity` struct wraps this with `Serialization_Header` (8 bytes) + `Entity_Data` + `Entity_Functions` (function pointers — NOT serialized).

**Impact:** The editor can serialize the known engine fields. Project-specific `Entity_Data` fields require C header parsing (see B-3). For initial implementation, serialize the engine-default `Entity_Data` and warn if the project overrides it.

### NB-4: Tile rendering in the workspace is unspecified

The spec never describes how tiles are visually represented in the editor.

**Impact:** Implement as colored rectangles keyed on `Tile_Kind` enum value. The `Tile_Kind` name can be displayed on hover.

### NB-5: Section 5 is missing

The spec jumps from section 4 to section 6. Likely reserved.

**Impact:** None.

### NB-6: Thread safety contract (section 4.2) is underspecified

**Impact:** Implement with `threading.Lock` guards on object access. Use `_`-prefixed methods for serialization-thread-only access.

### NB-7: Checksum algorithm for .tmp file validation is unspecified

**Impact:** Use `hashlib.sha256` from Python stdlib.

### NB-8: `Tile_Kind` and `Tile_Layer` enums in engine are essentially empty — populated by project

From the engine source:
- `tile_kind.h`: `None`, `Unknown`, with `GEN-LOGIC-BEGIN/END` and `GEN-NO-LOGIC-BEGIN/END` markers.
- `tile_layer.h` (from summary): `Default = 0`, with `GEN-BEGIN/END` markers.

The editor MUST parse the project-local versions of these headers to populate tile palettes.

**Impact:** Directly related to B-3. The enum parser must handle `GEN-*` markers.

### NB-9: GUI framework is imgui (confirmed)

The existing `tools/editor_ui_modules/message_hud.py` uses `imgui` (pyimgui). Use the same framework.

### NB-10: Multi-select behavior is underspecified

**Impact:** Implement multi-select visuals; restrict copy/paste to single. Defer bulk operations.

### NB-11: `Tile_Layer` vs `CHUNK__DEPTH` clarified

`CHUNK__QUANTITY_OF__TILES = CHUNK__WIDTH * CHUNK__HEIGHT * CHUNK__DEPTH = 8 * 8 * 2 = 128`

`Tile_Layer` is a separate concept from `CHUNK__DEPTH`. `CHUNK__DEPTH` is the Z-axis depth (number of vertical slices). `Tile_Layer` refers to rendering layers *within* a single tile (e.g., ground layer vs. cover layer), encoded as bitfields inside the `Tile` struct itself.

The tile indexing formula from `chunk.h` is:
```
index = x + ((CHUNK__HEIGHT - 1 - y) * CHUNK__WIDTH) + (CHUNK__WIDTH * CHUNK__HEIGHT * z)
```

Where `z` is the depth index (0 to `CHUNK__DEPTH - 1`), NOT the tile layer.

### NB-12: `world_directory.c` base64 encoding has a potential bug

In `append_base64_value_to__path`, the loop body uses `_base64_lexicon[value]` instead of `_base64_lexicon[b64]`. This appears to be an engine bug. The editor must replicate the *actual* path encoding behavior (bugs included) to find existing world files.

**Impact:** The editor's path generation must exactly match the engine's. Replicate the C logic faithfully in Python.

---

## Consistency Issues with Engine Code

### C-1: UUID sizes vary by context

- `Serialization_Header` uses `Identifier__u32` (32-bit UUID).
- `Serialization_Header__UUID_64` uses `Identifier__u64` (64-bit UUID).
- `Global_Space` and `Chunk` use `Serialization_Header__UUID_64`.
- `Entity`, `Inventory`, `Item_Stack`, `UI_Element` use `Serialization_Header` (32-bit).

The editor must use the correct UUID width per type.

### C-2: `Sprite_Animation_Kind` enum is nearly empty

Only has `None` and `Unknown`. Entity rendering in the editor will use colored rectangles initially (NB-4).

### C-3: Z-axis support is conditional on `LOCAL_SPACE_MANAGER__DEPTH`

From `local_space_manager.c`, Z-axis support is wrapped in `#if LOCAL_SPACE_MANAGER__DEPTH > 1`. When depth is 1, `_z__i32` is `#define`d to 0. The editor should support Z-axis navigation but gracefully handle depth=1 worlds.

### C-4: `Entity_Functions` contains function pointers that must NOT be serialized

The `Entity` struct contains `Entity_Functions` with 6 function pointers. These are runtime-only. The editor must serialize only `_serialization_header` + `entity_data`.

### C-5: `Game_Action` struct contains `#warning` directives

`defines.h` has active `#warning` directives inside the `Game_Action` struct, indicating it is still under development. The editor does not need to serialize `Game_Action` directly.

### C-6: Chunk directory path generation uses quad-tree descent

`world_directory.c` implements a 6-level quad-tree directory structure for chunk storage. The algorithm:
1. Mask chunk x,y to 8 bits: `x & 0xFF`, `y & 0xFF`
2. Start at center (128, 128, 128) with quad size 128
3. For 6 levels: descend left/right based on comparison, halving quad size
4. Create directory `c_<xx>_<yy>_<zz>` at each level (2-char hex per axis)
5. Final leaf directory contains the chunk files

### C-7: `CHUNK__HEIGHT` macro typo in `platform_defaults.h`

The macro is defined as `CHUNK_HEIGHT` (single underscore between CHUNK and HEIGHT) but used elsewhere as `CHUNK__HEIGHT` (double underscore). The editor should use numeric values from config, not try to resolve this inconsistency.

### C-8: `set_tile_of__chunk` uses different indexing than `get_p_tile_from__chunk`

In `chunk.h`, `set_tile_of__chunk` uses:
```c
index = (y << CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT) + (z << (CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT*2)) + x;
```
But `get_p_tile_from__chunk` uses:
```c
index = x + ((CHUNK__HEIGHT-1 - y) * CHUNK__WIDTH) + (CHUNK__WIDTH * CHUNK__HEIGHT * z);
```
These are NOT equivalent — `set_tile_of__chunk` does NOT invert Y. This is likely an engine bug. The editor should use the `get_p_tile_from__chunk` formula (Y-inverted) since that is the read path and is more likely to be correct for serialized data.

### C-9: Engine config override mechanism

`engine_config.h` is included by `platform_defaults.h` and allows projects to override ALL chunk/world constants. The file contains commented-out `#define` directives. Projects uncomment and set values as needed.

**Editor implication:** The editor MUST parse the project's `engine_config.h` (at `./include/config/implemented/engine_config.h` relative to project dir) to detect overridden constants. The parsing is simple:
- Look for uncommented `#define CONSTANT_NAME value` lines.
- For `BIT(n)` expressions, evaluate as `1 << n`.
- Fall back to `platform_defaults.h` defaults for any constant not overridden.

---

## Files Still Needed (nice-to-have)

| File | Reason | Priority |
|------|--------|----------|
| `examples/template-files/source/world/implemented/world/tile_logic_table_registrar.c` | Shows how tile logic tables are registered (needed for tile property editing). | Low — can defer tile logic editing. |
| Entity serialization source (e.g., `core/source/entity/entity_serialization.c` or similar) | Confirms exact binary format for entity `e` files. | Medium — needed for Entity Edit mode. |

---

## Recommended Implementation Order

1. **C enum parser + engine_config.h parser** (section 4.5) — needed by almost everything; parse `typedef enum { ... } Name;` patterns with `GEN-*` markers. Parse `#define` overrides from `engine_config.h`. Testable in isolation.
2. **Keybind system** (section 4.4) — self-contained, fully specified, testable.
3. **Message HUD extension** (section 1.5) — extend existing `message_hud.py` with SYSTEM level.
4. **Editor Mode / Tool framework** (sections 4.1.1, 4.1.2) — base classes, tab switching, tool selection.
5. **File Hierarchy HUD** (section 1.4) — uses world directory structure from `world_directory.c`.
6. **Workspace rendering skeleton** (section 4.2) — viewport panning, coordinate grid, placeholder tiles.
7. **World directory Python port** (section 4.3) — port `world_directory.c` path generation to Python.
8. **Chunk serialization** (section 4.3) — uses tile size from enum parser + chunk constants.
9. **Global_Space View mode** (section 1.1.1) — uses workspace + serialization.
10. **Chunk Edit mode** (section 1.1.2) — uses tile palette from enum parser + chunk serialization.
11. **Entity Edit mode** (section 1.1.3) — uses entity serialization.
12. **Container/Inventory Edit mode** (section 1.1.4) — defer (B-1).

---

## Key Technical Facts for Implementation

| Constant | Default Value | Overridable | Source |
|----------|---------------|-------------|--------|
| `CHUNK__WIDTH` | 8 (`BIT(3)`) | Yes, via `engine_config.h` | `platform_defaults.h` |
| `CHUNK__HEIGHT` | 8 (`BIT(3)`) | Yes, via `engine_config.h` (note: macro typo `CHUNK_HEIGHT`) | `platform_defaults.h` |
| `CHUNK__DEPTH` | 2 (`BIT(1)`) | Yes, via `engine_config.h` | `platform_defaults.h` |
| `CHUNK__QUANTITY_OF__TILES` | 128 (W×H×D) | Yes, via `engine_config.h` | `platform_defaults.h` |
| `LOCAL_SPACE_MANAGER__WIDTH` | 8 | Yes, via `engine_config.h` | `platform_defaults.h` |
| `LOCAL_SPACE_MANAGER__HEIGHT` | 8 | Yes, via `engine_config.h` | `platform_defaults.h` |
| `LOCAL_SPACE_MANAGER__DEPTH` | 1 | Yes, via `engine_config.h` | `platform_defaults.h` |
| `MAX_QUANTITY_OF__ENTITIES` | 128 | Yes, via `engine_config.h` | `platform_defaults.h` |
| `MAX_QUANTITY_OF__CLIENTS` | 4 | Yes, via `engine_config.h` | `platform_defaults.h` |
| `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | 3 (8px tiles) | Yes, via `engine_config.h` | `platform_defaults.h` |
| `sizeof(Tile)` | project-local, read from `array_of__tile_data__u8[N]` | N/A | template: 3 bytes |
| Tile index formula | `x + ((CHUNK__HEIGHT-1 - y) * CHUNK__WIDTH) + (CHUNK__WIDTH * CHUNK__HEIGHT * z)` | N/A | `chunk.h` |
| Y-axis | **Inverted** in memory (y=0 = bottom = last row block) | N/A | `chunk.h` |
| Chunk file | `t` (tiles), `e` (entities), `i` (inventories) | N/A | `world_directory.c` |
| UUID width (Entity) | 32-bit (`Serialization_Header`) | N/A | `defines.h` |
| UUID width (Chunk/Global_Space) | 64-bit (`Serialization_Header__UUID_64`) | N/A | `defines.h` |
| Endianness | Little-endian | N/A | NDS ARM + x86 targets |
| `Entity_Data` (engine default) | `{ Entity_Flags__u32; Entity_Kind; }` = 8 bytes | Yes, project-local | `entity_data.h` |
| `Entity` serialized | `Serialization_Header(8) + Entity_Data(8)` = 16 bytes min | N/A | `defines.h` |

---

## Summary

| Category | Count |
|----------|-------|
| BLOCKING | 3 (1 deferrable, 1 soft-blocking, 1 scoped/tractable) |
| RESOLVED | 3 |
| NON-BLOCKING | 12 |
| ENGINE CONSISTENCY | 9 |
| FILES NEEDED | 2 (nice-to-have) |

**Tractable blocker:** B-3 (C header parsing — scoped to enum parsing + `array_of__tile_data__u8[N]` extraction).

**Soft blocker:** B-2 (Properties HUD fields — derivable from engine source).

**Deferrable:** B-1 (Container/Inventory mode — spec says placeholder).

The UI framework, keybind system, enum parser, editor mode architecture, and world directory port can all begin immediately.

**Revision 4 note:** The spec has been updated to embed engine source file
references throughout. Future agents should derive all type definitions,
struct layouts, constants, and serialization formats from the referenced
engine source files rather than relying on hardcoded values in the spec
or report. If the engine source changes, the editor implementation should
be updated to match by consulting the referenced files.

**Revision 5 note:** Spec clarified that `Tile_Cover_Kind` is a project-
defined type, not an engine type. The editor discovers tile layer enum
types dynamically from the `GEN-RENDER-BEGIN` block in the project's
`tile.h`. Only `Tile_Kind` is guaranteed by the engine as the default
layer. Implementation begun: `c_enum.py`, `engine_config.py`,
`tile_parser.py` with full test suites.
