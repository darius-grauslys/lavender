# Lavender Tools v2 — Code Generation

> **Spec reference:** OVERVIEW.md S3.4  
> **Status:** DRAFT

## 1. GEN-Marker Protocol

### 1.1. Marker Format

GEN-markers are C line comments that delimit machine-managed regions in
source files.  The canonical format is:

```c
// GEN-{NAME}-BEGIN
... machine-managed content ...
// GEN-{NAME}-END
```

Where `{NAME}` is an uppercase identifier (e.g., `BEGIN`, `EXTERN`,
`LOGIC`, `NO_LOGIC`, `LOAD`, `UNLOAD`, `FRAME`, `FORWARD`,
`REGISTER-ANIMATIONS`, etc.).

### 1.2. Whitespace Rules

- Exactly one space between `//` and `GEN`.
- No trailing whitespace after `BEGIN` or `END`.
- Newline immediately after the marker comment.
- Content inside the block is indented according to the surrounding
  C context.

### 1.3. Nesting

GEN-markers do NOT nest.  A file may have multiple distinct marker pairs,
but they must not overlap.

### 1.4. Unnamed Markers

For backward compatibility, the default marker pair `// GEN-BEGIN` /
`// GEN-END` (no name component) is supported.  It is equivalent to
`GEN--BEGIN` / `GEN--END` internally.

## 2. Shared Parsing Library

### 2.1. The Problem

Tools v1 had **three independent GEN-marker parser implementations**:
- `mod_entity.py`: manual `str.find()` on `// GEN-BEGIN-BEGIN`
- `mod_scene.py`: manual `str.find()` on `// GEN-{NAME}-BEGIN`
- `scan_*.py`: `re.search(r'// GEN-BEGIN\n(.*?)// GEN-END', ...)`

These diverged in whitespace handling, error behavior, and supported
marker variants.

### 2.2. The Solution: `core/codegen.py`

A single module providing all GEN-marker operations:

```python
def find_gen_block(content: str, name: str = "") -> GenBlock | None:
    """Find a GEN-marker block by name.  CODEGEN.md S2.2

    Returns GenBlock with start_line, end_line, block_content,
    or None if not found.
    """

def append_to_gen_block(
    content: str, name: str, line: str, *, deduplicate: bool = True
) -> str:
    """Append a line to a GEN-marker block.  CODEGEN.md S2.2

    If deduplicate=True, skips insertion if the line already exists
    in the block.
    Returns the full file content with the line inserted.
    Raises GenBlockNotFoundError if the marker pair is missing.
    """

def replace_gen_block(content: str, name: str, new_content: str) -> str:
    """Replace the entire content of a GEN-marker block.  CODEGEN.md S2.2

    Raises GenBlockNotFoundError if the marker pair is missing.
    """

def clear_gen_block(content: str, name: str) -> str:
    """Remove all content from a GEN-marker block.  CODEGEN.md S2.2"""

def list_gen_blocks(content: str) -> list[GenBlock]:
    """List all GEN-marker blocks in a file.  CODEGEN.md S2.2"""
```

### 2.3. GenBlock

```python
@dataclass
class GenBlock:
    """CODEGEN.md S2.3"""
    name: str             # The marker name (empty string for unnamed)
    start_line: int       # 1-indexed line number of BEGIN marker
    end_line: int         # 1-indexed line number of END marker
    content: str          # Content between markers (excluding markers)
    indent: str           # Detected indentation of the block content
```

### 2.4. Error Handling

```python
class GenBlockNotFoundError(ToolError):
    """Raised when a GEN-marker block is not found.  CODEGEN.md S2.4"""
    def __init__(self, file_path: str, block_name: str):
        super().__init__(
            f"GEN block '{block_name}' not found in {file_path}",
            recoverable=False
        )
```

Missing or malformed markers are ERRORS, not silent skips.  Tools v1
silently skipped missing markers (e.g., `mod_scene._append_to_gen_marker`
printed a warning to stdout that was invisible in MCP JSON output).

## 3. C Code Generation Patterns

### 3.1. Template Approach

Tools v1 used massive f-string concatenation to generate C code (e.g.,
`gen_game_action.py` had 915 lines of string manipulation).

Tools v2 uses **template files** stored in `templates/`:

```
tools2/templates/
  entity/
    entity__NAME.h.template
    entity__NAME.c.template
  scene/
    scene__NAME.h.template
    scene__NAME.c.template
  ...
```

Templates use a simple `{{PLACEHOLDER}}` syntax.  The generator reads
the template, substitutes placeholders, and writes the result.

### 3.2. Template Substitution

```python
def render_template(
    template_path: Path,
    substitutions: dict[str, str],
) -> str:
    """Render a C code template.  CODEGEN.md S3.2

    Reads the template file, replaces all {{KEY}} placeholders
    with the corresponding values, and returns the result.
    Raises TemplateError if any placeholder is not substituted.
    """
```

### 3.3. Registrar Patching

Most `gen_*` tools need to append entries to registrar files (e.g.,
`entity_registrar.c`, `scene_registrar.c`).  This is always done via
`append_to_gen_block()` from S2.2.

The pattern is:
1. Read the registrar file.
2. Call `append_to_gen_block(content, "BEGIN", new_entry)`.
3. Write back via `write_atomic()`.

If includes are also needed, they are appended to a `GEN-INCLUDE` block
(or before the first non-comment line if no include block exists).

## 4. Ported Logic

### 4.1. What Is Ported

The C code generation LOGIC from tools v1 is ported verbatim where
correct.  This includes:

- Entity `.h`/`.c` boilerplate generation (gen_entity.py)
- Scene `.h`/`.c` boilerplate generation (gen_scene.py)
- Game action type hierarchy generation (gen_game_action.py)
- Tile layer layout derivation (gen_tile_layer.py)
- Sprite animation registration (gen_sprite.py)
- UI XML → C code generation (gen_ui_code.py)
- PNG generation/manipulation (gen_png.py, mod_png.py)

### 4.2. What Is Not Ported

- The subprocess dispatch architecture (replaced by ToolDef registry)
- The argparse CLI layer (replaced by Pydantic input models)
- The per-script tool_history integration (replaced by mandatory Transaction)
- The ad-hoc GEN-marker parsers (replaced by core/codegen.py)
- The duplicated helper functions (`_get_lavender_dir`, `read_file`, etc.)
