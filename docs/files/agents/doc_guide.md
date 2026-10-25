# Documentation Style Guide

Write module docs at the **surface level**: what the module does, its public API, and key files. Omit allocation details, step-by-step procedures, and failure codes unless they affect the caller. The goal is a compact reference that minimizes context strain and eliminates redundant sources of truth.

## Structure

### 1. Header line and sources

Start with a title line and a **Sources** line listing the primary files.

```markdown
# ModuleName — One-sentence description

**Sources:** `path/to/file.c` + `path/to/file.h`
```

List only the canonical source files. Do not enumerate every file or count lines in the header.

### 2. Surface Concerns (merge purpose + concerns)

A single section called **Surface Concerns**. It contains:

- A **one-paragraph** overview: what the module does, its layer in the architecture, and who calls it.
- **Bulleted entries**, one per concern. Each bullet is a single paragraph that names the concern and states its surface behavior. Use bold for the concern name.

```markdown
## Surface Concerns

The module does X. Layer: Y. Called from A, B, and C.

- **Concern name** — description of what it does and its interface contract.
- **Another concern** — more description.
```

**What to include:**
- What the module manages (types, pools, state)
- What the module does for callers (operations, their effect)
- Interface contracts (return values, notable failure modes)
- Cross-references to config knobs or dependent modules

**What to omit:**
- Allocation details beyond initialization requirements (`malloc`, pool sizing, pointer arrays)
- Step-by-step internal procedures (7-item numbered lists)
- Failure codes that do not affect the caller
- Redundant descriptions of behavior already stated in a bullet
- Separate "Purpose", "Place in Engine", "Concerns", or "Overview" sections

### 3. Public API Surface

#### Key Types

List each struct with its key members and where it is defined. One paragraph per struct with a bullet list of members.

```markdown
### Key Types

**`TypeName`** — defined in `header.h`. Key members:
- `member_type member_name` — short description.
```

#### Key Functions

List function signatures as code bullets. Include return values or notable return codes as short notes after the signature.

```markdown
### Key Functions

- `return_type function_name(params);` — returns bool.
- `Process *function_name(params);` — returns process or 0 on failure.
- `void function_name(params);`
```

Group related inlines (setter / getter pairs) on one bullet line where possible:
```markdown
- `static inline void set_client_as__active(Client *p_client);` / `bool is_client__active(Client *p_client);`
```

Remove trivial accessor inlines (e.g., `get_p_game_action_manager__inbound_from__client` that just returns `&p_client->field`).

**What to include:**
- All public-facing function signatures from headers
- Return values and notable return codes
- Parameter types

**What to omit:**
- Static/internal functions
- Inline getters that just return a field
- Function bodies or implementation details

### 4. Key Files Table

A table listing only the canonical files and their role. **No LOC column.**

```markdown
## Key Files Table

| File | Role |
|------|------|
| `core/source/client.c` | Client init, dispatch/receive/release, save/load processes, teleport |
| `core/include/client.h` | Client type, flags, dispatch/receive/release API, state inlines |
```

## Style Rules

1. **Prefer bullets over numbered lists.** Numbered lists imply ordering or procedure — use bullets for concerns, numbered lists only when order matters.
2. **One concern per bullet.** Each bullet should be self-contained and scannable.
3. **File names, not paths.** Use `core/source/file.c` not `/home/shalidor/Projects/Lavender/core/source/file.c`.
4. **File name only for line references.** When a line number is needed, write `in game.c` not `in game.c:152-189`.
5. **Cross-reference, don't duplicate.** If a concept appears in another module doc (e.g., config knobs, action managers), reference it with a link instead of restating it.
6. **No LOC column.** File capacity and line counts are volatile; they rot quickly. The role column is stable.
7. **No end-of-file line count footer.** `(End of file - total N lines)` is redundant.
8. **Keep it short.** Aim for under 80 lines. If a section is longer than 40 lines, it probably belongs in the module it describes.
9. **Bold the concern name** in each bullet: `**Concern name** — description`. This enables scanning.
10. **State return values explicitly** for non-void functions in the API section.

## Before / After Example

**Before** (old style, `world.md` at 222 lines):
- Separate sections for Purpose, Concerns (9 subsections), Key Flows (3 subsections), Dependencies (3 subsections), Cross-Cutting Concerns (7 items), Known Rough Edges (9 items)
- Step-by-step numbered procedures throughout
- LOC column in Key Files Table
- Line numbers on function references
- Redundant descriptions of the same concept across sections

**After** (refined style, `client.md` at 57 lines):
- Single "Surface Concerns" section — 7 bulleted concerns, no subsections
- No step-by-step procedures, no allocation details
- No Key Flows, Dependencies, or Cross-Cutting Concerns sections
- No LOC column, no line numbers on references
- Config knobs cross-referenced to `config.md` instead of repeated
- All API signatures retained with return values

The refined version conveys the same API surface and all surface-level concerns in ~25% of the lines, with zero lost information for a caller.
