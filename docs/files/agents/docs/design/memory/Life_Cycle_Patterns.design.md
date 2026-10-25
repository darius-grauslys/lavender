## 1. Overview

See ./docs/core/memory/Life_Cycle_Patterns.md for the currently tracked v1.0.0 documentation
for official memory life cycle patterns.

This document is tracking POST v1.0.0 considerations to the Life_Cycle_Patterns.md document.

## 2. Recommended Init / Dealloc Discipline

Lavender currently uses a **fused init** pattern: a single `initialize_X`
function serves as *both* the creation-time initializer **and** the
release-time reset. This conflates two distinct state transitions and is the
root cause of several findings in `aliased_texture` (see
`agents/core/design/include/rendering/aliased_texture.design.md`, F1/F4).

The target pattern **separates** the two operations and uses the
`IDENTIFIER_UNKNOWN` sentinel (§3) as the state discriminator:

1. **Manager initialization** — use the serialization-header functions
   (e.g. `initialize_serialization_header__contiguous_array`) to bring every
   slot's `uuid` to `IDENTIFIER_UNKNOWN` (the free state). This is the concrete
  , reliable way to establish a known initial state for a pool.

2. **Resource init** (`init_X`)
   - **Precondition:** `uuid == IDENTIFIER_UNKNOWN` (slot is free).
   - If `uuid != IDENTIFIER_UNKNOWN` → the resource is already initialized;
     **short-circuit out with an emitted error** (double-init detected).
   - Otherwise, initialize fields and assign a concrete `uuid`.

3. **Resource dealloc / reset** (`dealloc_X` / `reset_X`)
   - **Precondition:** `uuid != IDENTIFIER_UNKNOWN` (slot is allocated).
   - Tear down fields, then set `uuid` back to `IDENTIFIER_UNKNOWN`.

This makes init and dealloc **mutually exclusive** and makes each
**Idempotence**-checkable via the sentinel, removing the ambiguity of a fused
operation.

> **Timeline:** Adopting this discipline is a **large-scale refactor** and is
> **deferred to post v1.0.0**. Until then, the fused-init behavior and its
> hazards are **documented, not fixed**.

---
