# Module Design Checklist

Checklist for design analysis of Lavender engine modules.

*Note*: Struct definitions live in the monolithic `defines.h` and are visible to
all modules. Checks about struct exposure and opaque pointers apply primarily to
types declared in individual modules.

---

## 1. Layer Classification

Classify the module into one of six layers:

| Layer | Characteristics |
|-------|----------------|
| **Platform** | Direct OS/hardware access (`platform.h`, `PLATFORM_*` functions) |
| **Foundation** | Memory allocators, containers, math, string utilities, `defines.h` types |
| **Core** | Serialization, hashing, log, timer, random, world, process, entity, game_action |
| **Rendering** | Presentation subsystem: gfx context, textures, aliased textures, sprites, graphics windows, fonts, tile maps; builds on Core + `PLATFORM_*` handles, consumed by Domain and Application |
| **Domain** | Client, multiplayer, UI, inventory, collisions, scene, input |
| **Application** | Game loop, top-level orchestration (`game.h`, `client.h`) |

Then identify the module's role: **abstraction** (encapsulates concrete
subsystem details, deliberately surfacing a stable semantic to its upper-facing
interface) or **policy** (operates on the surfaced semantics of lower modules
to enact subsystem-wide or global pre/post conditions). Higher levels rely on
the module's abstraction; concrete changes below must not break that semantic.
If a concrete change would break abstraction, document the risk.

---

## 2. Dependency Direction

Who is allowed to know about whom. A pure graph property of `#include`s and calls.

| Check | Description |
|-------|-------------|
| 2.1 | Does the module only `#include` headers from its own layer or layers below it? Including a *higher*-layer header → **layer violation** |
| 2.2 | Does the module call into, or `#include`, any module that relies on *it*? → **Bidirectional dependency; flag for review** |
| 2.3 | Are there circular dependency chains at module level (A→B→C→A)? If so, has an abstraction been introduced to break the cycle? |
| 2.4 | Does the module include headers it doesn't directly use? |
| 2.5 | If the module uses a type or function from a non-adjacent layer, is there a documented reason (callback, configuration, platform abstraction)? |

---

## 3. Inversion of Control

How a lower module defers behavior upward *without* knowing its callers.

| Check | Description |
|-------|-------------|
| 3.1 | Are dependencies injected (passed as parameters) rather than hard-coded via `#include` + direct calls? |
| 3.2 | Are function pointers or vtable structs used to defer behavior to higher layers? (e.g., `m_game_action_handler__dispatch`) |
| 3.3 | If the module manages resources (memory pools, file handles), does it provide callbacks/hooks for the policy layer to customize behavior, rather than the policy layer reaching into the implementation? |
| 3.4 | Does the module expose a `get_*()` global singleton or `extern` global state? Are dependencies reached through globals instead of parameters? → **Hidden dependency; flag** |

---

## 4. Information Hiding

Two lenses on the same boundary: what the provider exposes, and what the caller reaches for.

### 4.1 Provider side (stratification)

| Check | Description |
|-------|-------------|
| 4.1.1 | Does the header expose only what public API consumers need? Are private structs and internal functions confined to the `.c` file? |
| 4.1.2 | If header-only, is that a deliberate choice (inline optimization, compile-time computation)? If implementation-only, are symbols exported only via a registration/factory mechanism? |

### 4.2 Caller side (Law of Demeter)

| Check | Description |
|-------|-------------|
| 4.2.1 | Does any function chain more than one `->`/`.` access through objects from *different* modules? (e.g., `get_p_world_from__game(p_game)->p_some_field`) → **Flag** |
| 4.2.2 | Does any function reach through a singleton/manager to a nested resource? (e.g., `get_game()->renderer->texture_pool->textures[0]`) → **Strong violation** |
| 4.2.3 | Do accessor functions chain through intermediate objects (Game→World→Inventory_Manager)? → **Check if justified by Domain layering** |
| 4.2.4 | Does a function accept a struct pointer and access its fields directly across module boundaries, or expose types from modules that are not direct dependencies? |

---

## 5. Cohesion

Does the module do one thing?

| Check | Description |
|-------|-------------|
| 5.1 | Can the module's responsibility be stated in one sentence without "and"? |
| 5.2 | Do all public functions operate on the same core data/concept? Functions that never touch the module's central types → **candidate for extraction** |
| 5.3 | Do unrelated call-sites depend on the module for *different* subsets of its API? → **candidate for splitting** |

---

## 6. Ownership & Lifetime

Who allocates, who frees, and in what order.

| Check | Description |
|-------|-------------|
| 6.1 | For every resource the module creates, is the owner (the code responsible for release) unambiguous? Are create/destroy, init/deinit pairs symmetric and in the same module? |
| 6.2 | Do returned pointers document whether the caller borrows or owns them? |
| 6.3 | Does init/shutdown ordering across modules form a clean stack (deinit in reverse init order), or are there hidden ordering constraints? |

---

## 7. Temporal Coupling & API Contracts

Constraints on *when* and *in what order* the API may be used.

| Check | Description |
|-------|-------------|
| 7.1 | Must callers invoke functions in a specific order (init before use, X before Y)? Is that enforced (assert/error) or merely implied? |
| 7.2 | Are preconditions and postconditions of public functions checkable or documented? |
| 7.3 | Are init/shutdown idempotent or protected against double-invocation? |

---

## 8. Concurrency Assumptions

| Check | Description |
|-------|-------------|
| 8.1 | Which thread(s) may call this module? Is that stated anywhere? |
| 8.2 | Does the module hold mutable static/global state that would break under concurrent callers? |
| 8.3 | Are callbacks invoked on the same thread as registration, and do callback consumers assume so? |

---

## 9. Error Boundary Consistency

| Check | Description |
|-------|-------------|
| 9.1 | Does the module use one consistent error convention (return codes, out-params, logging, asserts)? Does it match adjacent modules in its layer? |
| 9.2 | Are errors propagated upward to the policy layer, or silently swallowed at the abstraction layer? |
| 9.3 | On failure mid-operation, is state left valid (no partial initialization leaks)? |

---

## 10. Stability & Change Impact

Lower layers should be stable; volatility belongs at the top.

| Check | Description |
|-------|-------------|
| 10.1 | Does the public interface change frequently? If so, is the module at the appropriate layer? |
| 10.2 | If a public function signature changes, how many call sites break? If a struct field is removed/renamed, how many modules break? |
| 10.3 | Depended-upon-by-many + depends-on-many → **highest-risk module; flag for decomposition** |
| 10.4 | Are there tests or documentation that pin the current public interface? (Score only on references that actually exist — see the spec-reconstruction note below.) |

> **Spec reconstruction (context for 10.4):** Specs under `docs/specs/` are being
> **rebuilt**. The prior auto-generated specs — and any test comment citing a
> `docs/specs/.../*.spec.md` path — were produced in a flawed automated manner.
> A **dangling spec reference** (a cited spec file that does not exist) is a
> known, in-progress condition of the reconstruction: **treat it as a known gap,
> not a defect of the module under review.** Score 10.4 only on whether the
> *interface* is pinned by tests/docs that actually exist.

---

## 11. Design Output & Documentation Tracking

Where a design pass writes its results, and how the two documentation trees are
kept in sync.

### 11.1 The design record: `*.design.md`

The **required** output of a module design pass is a **design record** written
to `./agents/core/design/[...]/<module>.design.md`, where **`[...]` mirrors the
module's sub-path relative to `./core`**.

> **Mapping rule:** take the module header's path, strip the `core/` prefix, and
> re-root the remainder under `./agents/core/design/`. The record is named for
> the module stem (`<stem>.design.md`).
>
> | Module (under `./core`) | Design record |
> |--------------------------|---------------|
> | `include/rendering/aliased_texture.h` | `agents/core/design/include/rendering/aliased_texture.design.md` |
> | `source/world/region_manager.c` (no `.h`) | `agents/core/design/source/world/region_manager.design.md` |
>
> For a paired module, mirror the **header's** path; for an
> implementation-only module (no `.h`), mirror the **`.c`'s** path.

The design record is the **Single Source of Truth (SSOT)** for the module's
findings, concerns, and decisions. It is the only *required* written artifact of
a pass.

### 11.2 The two documentation trees

Design knowledge lives in two trees with a **dual nature**:

| Tree | Nature | Holds |
|------|--------|-------|
| `./docs/...` | **Current** — indicative of Lavender as it *is* today (tracked to v1.0.0) | SSOT reference docs for current conventions (e.g., `docs/core/memory/Life_Cycle_Patterns.md`) |
| `./agents/docs/design/...` | **Design** — *post*-v1.0.0 considerations; what Lavender *could* become | `.design.md` companions tracking forward-looking proposals against a `./docs` topic (e.g., `agents/docs/design/memory/Life_Cycle_Patterns.design.md`) |

A `./agents/docs/design/<topic>.design.md` **references** its current-state
counterpart in `./docs/...` and records only the design considerations that are
*not yet* indicative of the current engine.

### 11.3 Updating the documentation trees (tracking rule)

Producing or editing `./docs` output is **NOT required** as part of a design
pass. The obligations are:

1. **Update in place** — if a finding is *deemed relevant* to an existing `./docs`
   reference, update that reference so it remains the accurate SSOT.
2. **Record as a concern** — if a finding implies that a *new* `./docs` file
   should exist, do **not** create it during the pass. Instead, **list it as a
   concern in the module's `*.design.md`** record (§11.1).

The same split applies to `./agents/docs/design/`: cross-cutting / topic-level
design considerations that do not belong in a single module's `*.design.md` are
tracked in the matching `./agents/docs/design/<topic>.design.md`.

> **Net rule:** the module `*.design.md` is always produced; `./docs` and
> `./agents/docs/design/` are updated only when relevant, and any *new* file
> they would need is surfaced as a concern in the `*.design.md` rather than
> created ad hoc.
