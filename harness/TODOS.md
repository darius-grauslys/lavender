# TODOS — harness

Backlog for the gdb QA harness. Ordered roughly by when we intend to pick
each item up. The **focus of the current session** is items **1** and **2**
(the `DebugScannerBase` redesign + the subtypes that accommodate it) plus
the **batched GDB calls** optimization.

> Note: `harness_qa.py` is **obsolete** and should be ignored. The harness is
> the modular package under `harness/` (see `__init__.py`). `AGENTS.md` is
> stale — it still documents the old monolithic `harness_qa.py`; it needs a
> rewrite to match the modular structure (see "Housekeeping" below).

---

## 1. `DebugScannerBase` redesign — expose state as a JSON table  ✅ (this session)

Give `DebugScannerBase` a uniform, Liskov-safe surface over the gdb scanner
state:

- `get_fields() -> list[str]`
  Top-level field names the table exposes (the keys of `get_table()`).
- `get_table() -> json`
  A **JSON-parsable** nested snapshot of the scanner state (a dict of
  `str/dict/list/int/bool/None`). **Not** uniformly schema'd across subtypes —
  the only Liskov sub-invariant is that *every* subtype returns something
  `json.dumps` can serialize. Subtypes customize this via the `_enrich_table()`
  hook; the base reads the top-level struct fields.
- `get_field(demeter: str) -> json`
  **Law of Demeter** navigation: walk the JSON object returned by `get_table()`
  along the dot-path `demeter` (e.g. `"ui_managers.0.ui_elements.1.uuid"`) and
  return the value at that path. Returns a JSON value (a `str` for a leaf gdb
  value, a `dict` for a nested node). Raises `KeyError` for an unknown demeter.
- `find_demeters(substring: str) -> list[str]`
  Greps the `get_table()` JSON for a substring across **keys** and returns the
  list of valid `demeter` dot-paths that point at matches. This is the
  discovery primitive: `find_demeters("uuid")` → every `...uuid` path in the
  table.

Implementation notes (settled in this session):
- The table is **cached** after the first `get_table()` and invalidated on
  `get_scanner()` / `_advance()` so `get_field()` / `find_demeters()` do not
  re-query gdb on every call.
- C struct members accessed by a chained gdb expression (e.g.
  `_serialization_header.uuid`) are stored as **nested JSON** so that the
  dot-path of a `demeter` lines up 1:1 with the table structure.
- `get_table()` must be called **after** `get_scanner()` (the convenience
  variable only exists once the struct has been captured by value).

## 2. Update the scanner subtypes to the new base  ✅ (this session)

- **`DebugUIScanner`** (the "iterating manager" case): `get_table()` maps
  **by `ui_manager` pointer**, then each `ui_manager` **sub-maps to each `ui_element`**:

  ```
  {
    <DEBUG_UI_Scanner top-level fields ...>,
    "ui_managers": {
      "0x1234": {
        "uuid": "0xAAAA",
        "quantity_of__ui_elements": 2,
        "ui_elements": {
          "0x2000": {"uuid": "0x...", "kind": "UI_Element_Kind__Button"},
          "0x2100": {"uuid": "0x...", "kind": "UI_Element_Kind__Slider"}
        }
      }
    }
  }
  ```
  Scanners only *present* the gdb state as JSON; they do not interpret it.
  This is what makes item 3 possible later.

- **Batched GDB calls** ✅ (this session): `get_table()` composes a single
  `call {((FUNC)$s.m_next_manager)(), ((FUNC)$s.m_next_element)(), ...}`
  expression to visit all allocated managers and their elements in one gdb
  round-trip, dramatically reducing overhead (similar to ADB on Android).

 - **`DebugEntityScanner`**: `get_table()` maps each **Entity pointer** to
   `{"uuid": <hex>, "kind": <enum name>}`, using batched `m_next_entity` calls:

   ```
   {
     <DEBUG_Entity_Scanner top-level fields ...>,
     "entities": {
       "0x2000": {"uuid": "0xE0001", "kind": "Entity_Kind__None"},
       "0x2100": {"uuid": "0xE0002", "kind": "Entity_Kind__Unknown"}
     }
   }
   ```

 - **`DebugSceneScanner`**: `get_table()` maps each **Scene pointer** to
   `{"kind": <enum name>}`, using batched `m_iterate_scene` calls:

   ```
   {
     <DEBUG_Scene_Scanner top-level fields ...>,
     "scenes": {
       "0x4000": {"kind": "Scene_Kind__None"},
       "0x5000": {"kind": "Scene_Kind__Unknown"}
     }
   }
   ```
   Note: `DEBUG_Scene_Scanner` has no UUID field — scenes are identified by
   pointer/kind, not a UUID.

## 3. (Future) Search a Hitbox / Inventory component by UUID  ⬜

Support looking up a **Hitbox component by UUID** and an **Inventory component
by UUID**.

- **Out of scope for the scanners.** This will be a **util module** — one for
  hitbox, one for inventory — that consumes the JSON `get_table()` (and
  `find_demeters()`) rather than living in `DebugScannerBase` or a scanner
  subtype.
- Depends on item 1's `find_demeters()` / `get_table()` being available.

## 4. (Future) `dispatch_click` mode argument  ⬜

`DebugInputDriver.dispatch_click()` should take a **`mode`** argument instead
of a bare bool, so we can grow more complex dispatch behavior later without
another signature churn. Initial modes:

- `"fire-forget"` — dispatch and return immediately.
- `"break"` — dispatch, then break at the spawned process's
  `complete_process()` (the documented workflow in `drive_input.h`).

Model as an enum/string-union of modes, not a bool.

## 5. (Future) Wrap `gl_debug_screencap()` in a GL harness module  ⬜

Wrap the screenshot helper in a new `harness` module (a GL driver, alongside
`DebugInputDriver`).

- **Correction to the original note:** `gl_debug_screencap()` is declared in
  `sdl/include/debug/opengl/gl_debug_screen.h`, **not** `gl_debug.h`
  (`gl_debug.h` only declares `GL_debug_init`).
- Signatures to wrap:
  - `bool gl_debug_screencap(Game *p_game)` → writes `./build/sdl/screen.png`.
  - `bool gl_debug_screencap__framebuffer(Game *p_game, GL_Framebuffer *p_gl_framebuffer)`.
- Returns `bool`; the value only surfaces in the gdb console stream, so parse
  it like `dispatch_click` does today (see `lavender_debug._extract_call_value`).
- `#ifndef NDEBUG` guarded — absent in release builds.

---

## 6. (Known issue) Pointer-to-pointer vs single indirection for UI elements  🿡

`DEBUG_UI_Scanner` has both `p_ptr_ui_element__current` (UI_Element **) and
`p_ui_element__current` (UI_Element *).  The scanner table uses the single
indirection pointer `p_ui_element__current` as the element key.  This is
the `UI_Element *` that callers (like `DebugUIUtils`) use directly to invoke
handler fields via `->`, without needing to dereference.

The mock in `verify_driver.py` simplifies this by having `p_ptr_ui_element__current`
return the element pointer directly (the mock doesn't simulate memory).

## 7. (Known issue) Implicit step during UI handler invocation

When `ui utils <handler>` invokes a function pointer via `call`, gdb may
implicitly step into the handler function, moving the current frame away from
`poll_ui_manager__update`.  This is the same behavior observed when manually
driving gdb commands — it's a gdb characteristic, not a harness bug.

`DebugUIUtils` already handles this: after each handler invocation, it checks
the current frame via `-stack-info-frame` and issues `-exec-finish` (followed
by `-stack-select-frame 0`) if the frame changed.  However, if multiple
handlers are invoked in sequence and the frame is already `poll_ui_manager__update`,
`finish` may need a conditional guard to avoid stepping out of the function
prematurely.  Track and refine as needed.

## Housekeeping

- **`AGENTS.md` is stale.** It documents the obsolete `harness_qa.py`
  monolith and the `DebugUIScannerExplorer` helper. Rewrite it to document the
  modular package (base + subtypes + input driver + frame controller) and the
  new table/demeter API from item 1.
- `harness_qa.py` should be deleted once `AGENTS.md` no longer references it.
- `gdb_mcp.py` / `harness.py` skeletons still name the old
  `read_field` / `read_fields` API in comments; update when they get built out.

## Verifying

```
python3 -m harness.verify_driver
python3 -m py_compile harness/debug_scanner.py harness/debug_scanner_ui.py \
    harness/debug_scanner_entity.py harness/debug_scanner_scene.py
```

`verify_driver.py` drives every scanner against a `FakeGdbmi` stub and asserts
the exact gdb command strings and the shape of the resulting JSON tables.
