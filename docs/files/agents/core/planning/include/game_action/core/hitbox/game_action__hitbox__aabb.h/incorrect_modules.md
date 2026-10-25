# Planning: game_action__hitbox__aabb.h — Incorrect Modules

**Review source:** `agents/core/review/include/game_action/core/hitbox/game_action__hitbox__aabb.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/game_action/core/hitbox/game_action__hitbox__aabb.h`
- `core/source/game_action/core/hitbox/game_action__hitbox.c`
- `core/include/collisions/core/aabb/hitbox_aabb_manager.h`
- `core/source/collisions/core/aabb/hitbox_aabb_manager.c`

---

## 1. Problem Identification

**Function:** `m_process__game_action__hitbox__aabb` (lines 12–75 of `core/include/game_action/core/hitbox/game_action__hitbox__aabb.h`)

**Defect:** Missing null check on `p_hitbox_aabb` after retrieval via `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager`.

The manager pointer (`p_hitbox_aabb_manager`) is validated in debug builds, but the retrieved hitbox pointer is never validated in any build. When the target UUID does not correspond to an allocated hitbox, `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager` returns null (its implementation delegates to `dehash_identitier_u32_in__contigious_array`, which can return null for unoccupied slots). The subsequent calls to `get_position_3i32F4_of__hitbox_aabb`, `set_hitbox_aabb__position_with__3i32F4`, `set_velocity_to__hitbox_aabb`, and `set_acceleration_to__hitbox_aabb` all dereference the null pointer, causing undefined behavior.

This is a **Boundary Condition** violation: the function's **Precondition** (item 5 in the documented contract) states the UUID must reference a valid hitbox, but the implementation does not enforce this as an **Assertion** — it simply proceeds and crashes. The sibling function `m_process__game_action__hitbox` in `game_action__hitbox.c` correctly guards with a null check on `pV_hitbox` before use, establishing the expected validation pattern.

## 2. Impact Assessment

**Direct scope:** The function is header-only (defined in `.h`, no corresponding `.c`). No callers were found in `./core/source` or `./tests` that directly invoke `m_process__game_action__hitbox__aabb`. It appears to be a standalone process handler intended for registration into a `Game_Action_Logic_Table`, but no registration function exists in the current codebase.

**Coupled assumptions:**
- The function's **Postcondition** (items 1–5) assumes `p_hitbox_aabb` is always non-null. Correcting the defect by adding a null check introduces a new failure path (fail_process + early return) that is not currently reflected in the documented postconditions.
- The `#ifndef NDEBUG` guard on the manager null check implies the manager is assumed non-null in release builds. If the manager is null in release, the function proceeds to call `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager` with a null manager — which itself returns null (in debug) or undefined behavior (in release). The new hitbox null check would partially mask this, but the root cause (unguarded manager in release) remains.
- `poll_for_collision_node_update` is called with `GET_UUID_P(p_hitbox_aabb)` — if `p_hitbox_aabb` is null, the UUID extraction is itself a null dereference. The null check must precede this call.

**Blast radius:** Low. The function has no known external callers or dependents that rely on the broken (crashing) behavior. No de facto contract is invalidated by adding the guard.

## 3. Resolution Assessment

### Step 1: Add null check on `p_hitbox_aabb`

In `m_process__game_action__hitbox__aabb`, immediately after the call to `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager`, insert:

```c
if (!p_hitbox_aabb) {
    debug_error("m_process__game_action__hitbox__aabb, p_hitbox_aabb == 0.");
    fail_process(p_this_process);
    return;
}
```

This check should be **unconditional** (not gated behind `#ifndef NDEBUG`), matching the pattern in `m_process__game_action__hitbox` where the null check on `pV_hitbox` is always active. This makes the **Precondition** (valid UUID) enforceable at runtime and converts a silent crash into a controlled process failure.

### Step 2: Evaluate manager null-check gating

Consider whether the `#ifndef NDEBUG` guard on `p_hitbox_aabb_manager` should also be made unconditional. The current gating means release builds will pass a null manager to the lookup function, producing undefined behavior. If the manager is contractually guaranteed non-null in release (e.g., by an upstream invariant), document this explicitly. Otherwise, promote the check to unconditional.

### Step 3: Update documented postconditions

Add a new postcondition entry:
> 6. If `p_hitbox_aabb` is null (target UUID not found), the process is failed via `fail_process` and the function returns early without mutating any hitbox state or calling `poll_for_collision_node_update`.

### Step 4: Test coverage

No existing tests reference `m_process__game_action__hitbox__aabb`. The test suite in `tests/core/source/game_action/core/hitbox/` covers only `game_action__hitbox.c`.

**New tests needed:**
- **Property Based Testing**: Generate random UUIDs (including unallocated ones) and verify that `m_process__game_action__hitbox__aabb` fails the process gracefully (no crash, process state is FAILED) when the UUID is not present in the manager.
- **Fuzzing**: Feed malformed or edge-case UUIDs (0, MAX_UINT32, values beyond pool size) to confirm no null dereference occurs.
- **Equivalence Check**: Verify that for a valid UUID, the post-fix function produces identical hitbox state and collision node updates as the pre-fix function (behavior preservation for the happy path).

### Step 5: Caller updates

No callers require updating. The fix is internal to the function and changes only its failure-mode behavior (from UB/crash to controlled process failure).

## 4. Test Verification Checklist

| Aspect | Finding |
|--------|---------|
| Existing tests for `m_process__game_action__hitbox__aabb` | None found |
| Existing tests asserting broken behavior | None (no tests exist) |
| New tests needed | Yes — null-UUID failure path, valid-UUID happy path, boundary UUIDs |
| Recommended strategy | Property Based Testing + Fuzzing for the null path; Equivalence Check for happy-path preservation |
| Test impact blast radius | **Low** — only new test cases needed; no existing assertions invalidated |

## 5. Blast Radius Summary

- **Files changed:** 1 (`core/include/game_action/core/hitbox/game_action__hitbox__aabb.h`)
- **Behavior-preserving for current callers:** Yes — no callers exist; happy path is unchanged
- **Phased approach needed:** No — single localized fix
- **De facto contracts invalidated:** None
