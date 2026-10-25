# Planning: local_space.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/local_space.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/local_space.h`
- `core/source/world/local_space.c`
- `core/include/world/global_space.h` (downstream callee of the accessor)
- `core/source/world/global_space.c` (callers of the global-space accessor)
- `tests/core/source/world/test_suite_world_local_space.c` (existing coverage)

---

## 1. Problem Identification

Two functions flagged **Incorrect**. Both are null-safety defects on pointer
delegation chains; both produce undefined behavior (null pointer dereference)
in valid runtime states rather than honoring their documented contract.

### `poll_for__collisions` — `core/source/world/local_space.c`
- **Defect:** the four diagonal neighbor accesses (NE, NW, SE, SW) chain two
  pointer dereferences with no intermediate null guard, e.g.
  `p_local_space->p_local_space__north->p_local_space__east`. When the
  intermediate cardinal pointer is `NULL` — a valid state for edge/corner local
  spaces — the second hop dereferences null (undefined behavior). The four
  cardinal accesses are safe because they pass the neighbor pointer directly to
  `get_p_collision_node_from__local_space`, which already returns `0` on null.
- **Terminology:** a violated **Precondition** is being enforced by the caller
  ("neighbor pointers are valid or NULL") but the code only honors it for the
  cardinal hops; the diagonal hops ignore the **Boundary Condition** of a missing
  neighbor. The function therefore fails its own postcondition (poll all 9 nodes
  safely) at spatial boundaries.

### `get_p_collision_node_from__local_space` — `core/include/world/local_space.h`
- **Defect:** the accessor null-checks `p_local_space` but then delegates to
  `get_p_collision_node_from__global_space(get_p_global_space_from__local_space(...))`.
  The callee (`global_space.h`, line 210) does **not** null-check its parameter — it
  returns `p_global_space->p_collision_node` directly. So a non-null local space
  whose `p_global_space` is `NULL` dereferences null (undefined behavior).
- **Terminology:** the accessor's advertised contract ("return `0` for a null
  input; never crash") is a broken **Postcondition** for the null-global-space
  branch. This is also a consistency/DRY defect: the sibling
  `get_p_chunk_from__global_space` (line 194) *does* guard `p_global_space` before
  dereferencing, so the collision-node accessor is an outlier against the shared
  **Single Source of Truth** accessor pattern.

---

## 2. Impact Assessment

### Callers coupled to the broken behavior

- **`poll_for__collisions`:** public entry point for collision polling of a local
  space + its 8 neighbors (declared in `local_space.h`; invoked from the world/game
  update loop). Its callers assume it is safe to call on any loaded local space.
  Today that assumption is only true for interior spaces; at any boundary where a
  cardinal neighbor is absent, the current code already risks a crash. Callers that
  "work" today are doing so only because their tested spatial layouts happen to
  keep cardinal neighbors non-null — a **de facto contract** built on luck, not on
  the code. Correcting the diagonal guards makes boundary polling safe; interior
  behavior is unchanged (behavior-preserving).

- **`get_p_collision_node_from__local_space`:** inline accessor used by all nine
  calls inside `poll_for__collisions` and available to any other caller. For a
  non-null `p_global_space` the corrected version returns an identical value, so
  every current caller that passes a fully-linked local space is unaffected. Only
  the null-`p_global_space` branch changes — from undefined behavior to returning
  `0`, which is exactly what the accessor's null-`p_local_space` branch already
  promises. No caller can be relying on the dereference as a feature.

### Downstream ripple of fixing the global-space accessor (SSOT option)

If the null guard is added in `get_p_collision_node_from__global_space` itself
(the recommended SSOT fix, aligning it with its chunk sibling), the change also
protects the other direct callers in `core/source/world/global_space.c`
(lines 63, 132, 393, 444). Those call sites currently pass a `p_global_space`
they assume non-null; making the accessor total (return `0` on null) is
behavior-preserving for them in the valid case and removes a latent crash in the
invalid case. No signature changes propagate outward.

### Assumptions invalidated by the fix

- The implicit "cardinal neighbors are always present" assumption behind the
  diagonal hops is removed; boundary spaces become a first-class, handled case.
- The implicit "local space always has a linked global space" assumption behind
  the collision-node accessor is made explicit and guarded.

---

## 3. Resolution Assessment

### Fix A — `poll_for__collisions` (diagonal null guards)
1. For each diagonal hop, resolve the intermediate cardinal pointer once into a
   local variable, then only perform the second hop when it is non-null:
   - `Local_Space *n = p_local_space->p_local_space__north;` → pass
     `(n ? n->p_local_space__east : 0)` for NE, `(n ? n->p_local_space__west : 0)`
     for NW.
   - Same pattern on `p_local_space__south` for SE / SW.
2. Passing `0` is safe because `get_p_collision_node_from__local_space` already
   returns `0` on a null input, and the downstream
   `poll_for__collisions_within_this__collision_node` already null-checks its node.
3. **Callers:** signature unchanged → no caller updates required. Behavior is
   preserved for interior spaces and becomes safe at boundaries.
4. (Optional refactor) Extract a small static helper that resolves a neighbor by
   offset with a single null guard, to keep the nine blocks DRY and prevent the
   same defect recurring.

### Fix B — `get_p_collision_node_from__local_space` / global-space accessor
1. **Preferred (SSOT):** add the null guard inside
   `get_p_collision_node_from__global_space` in `core/include/world/global_space.h`,
   mirroring `get_p_chunk_from__global_space`:
   ```c
   if (p_global_space) return p_global_space->p_collision_node;
   return 0;
   ```
   This makes the accessor total, closes the crash, and aligns the collision-node
   accessor with its chunk sibling (removes the DRY/consistency outlier). It also
   hardens the four `global_space.c` call sites noted above.
2. **Alternative (local):** if touching `global_space.h` is out of scope for this
   module, guard the intermediate in `get_p_collision_node_from__local_space`:
   fetch `Global_Space *gs = get_p_global_space_from__local_space(p_local_space)`
   and only call the global accessor when `gs` is non-null. This fixes the flagged
   function but leaves the shared accessor still unsafe for other callers — so the
   SSOT option is recommended.
3. **Callers:** no signature change either way; valid-case behavior unchanged.

### Documentation / contract
- Update the accessor's stated contract to reflect that a non-null local space with
  a null global space yields `0` (not undefined behavior). Keep the documented
  preconditions/postconditions of `poll_for__collisions` accurate for boundary
  spaces.

---

## 4. Test Verification Checklist

**Existing coverage:** `tests/core/source/world/test_suite_world_local_space.c`
covers `get_p_global_space_from__local_space` and the allocation/active predicates,
but has **no** assertions for `get_p_collision_node_from__local_space` or
`poll_for__collisions`. Neither flagged function is exercised today, so the fix is
not invalidated by existing assertions — but it is also not protected. New tests
are required.

- **`get_p_collision_node_from__local_space`:**
  - null local space → `0` (guards the existing branch).
  - non-null local space with `p_global_space == NULL` → `0`, no crash (the newly
    fixed boundary; this is the regression case).
  - non-null local space with a valid global space → returns that global space's
    collision node.
  - **Equivalence Check** against the sibling `get_p_chunk_from__local_space` /
    `get_p_chunk_from__global_space` null-handling to lock in the consistency fix.

- **`poll_for__collisions`:**
  - interior space with all 8 neighbors present → collision handler invoked for all
    9 nodes (center + 8), excluding the tested hitbox itself (**Equivalence Check**).
  - boundary/corner space with some cardinal neighbors `NULL` → no crash; handler
    invoked only for the nodes that actually exist (**Property Based Testing** over
    the neighbor-null combinations, i.e. **Fuzzing** of the 2^6 neighbor presence
    space with a bounded sample).
  - **Round Trip Check**: place a hitbox in a neighbor node, poll, assert the handler
    fires exactly once for that pair (stateful detection round-trips).

**Test blast radius:** Low. No existing assertions change; additions are isolated to
the local-space test suite (plus a small global-space accessor null case if the SSOT
fix is taken). No phased rollout of tests is required.

---

## 5. Blast Radius Summary

- **Files changed:** 2 minimum — `core/source/world/local_space.c` (Fix A) and
  `core/include/world/global_space.h` (Fix B, SSOT). If the local-guard alternative
  is chosen instead, the change is confined to `core/include/world/local_space.h`.
  Test file additions: `tests/core/source/world/test_suite_world_local_space.c`
  (and optionally a global-space test).
- **Behavior-preserving for current callers:** Yes. All changes alter only the
  undefined-behavior branches; the valid-case return values and the collision-poll
  contract are unchanged.
- **Phased approach:** Not strictly required, but recommended ordering — (1) apply
  the global-space accessor null guard (SSOT, also hardens `global_space.c`), then
  (2) add the diagonal guards in `poll_for__collisions`, then (3) add tests. Each
  step is independently safe.
- **De facto contracts invalidated:** The two implicit "always-linked" assumptions
  (cardinal neighbors present; global space linked) are replaced with explicit,
  guarded handling. No legitimate caller relies on the crash or the unguarded
  dereference, so no real contract is broken.
