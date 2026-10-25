# set_hitbox_aabb_as__dirty

- **Function name:** `set_hitbox_aabb_as__dirty`
- **File of origin:** `core/include/collisions/core/aabb/hitbox_aabb.h` (lines 108-111)

---

## 2. Semantic

Sets the `HITBOX_FLAG__IS_DIRTY` bit in a `Hitbox_AABB`'s `hitbox_aabb_flags__u8` field, marking the hitbox as "dirty" (i.e., its collision/AABB state has changed and needs re-computation before it can be used in collision checks).

```c
static inline
bool set_hitbox_aabb_as__dirty(Hitbox_AABB *p_hitbox_aabb) {
    return set_hitbox_flags_as__dirty(&p_hitbox_aabb->hitbox_aabb_flags__u8);
}
```

This is a thin wrapper that delegates to `set_hitbox_flags_as__dirty(Hitbox_Flags__u8 *p_hitbox_flags__u8)` in `core/include/collisions/hitbox.h` (lines 12-17):

```c
static inline
bool set_hitbox_flags_as__dirty(Hitbox_Flags__u8 *p_hitbox_flags__u8) {
    return *p_hitbox_flags__u8 |=
        HITBOX_FLAG__IS_DIRTY
        ;
}
```

Where `Hitbox_Flags__u8` is `u8` (`defines.h:329`) and `HITBOX_FLAG__IS_DIRTY` is `BIT(1)` (`defines.h:332`). The compound assignment `|=` evaluates to the new value stored, so the function returns the full flag byte coerced to `bool`; because the dirty bit was just set, the result is always true.

---

## 3. Pre-conditions

1. `p_hitbox_aabb` must be a non-null pointer to a valid, initialized `Hitbox_AABB` struct (`defines.h:450-458`).
2. The `hitbox_aabb_flags__u8` field of the struct must be readable and writable.

---

## 4. Post-conditions

1. The `HITBOX_FLAG__IS_DIRTY` bit (bit 1) in `p_hitbox_aabb->hitbox_aabb_flags__u8` is set (1); all other flag bits are unchanged.
2. Returns `true` — a `bool` coerced from the post-assignment flag byte, which is guaranteed nonzero because the dirty bit was just set.

---

## 5. Correctness Verdict

**Correct.**

---

## 6. Semantic Alignment

The implementation fulfills the semantic intent: it marks a hitbox AABB as dirty so the collision system knows its state is stale and requires re-computation. The delegation chain `set_hitbox_aabb_as__dirty` → `set_hitbox_flags_as__dirty` → `*p_hitbox_flags__u8 |= HITBOX_FLAG__IS_DIRTY` correctly performs a bitwise-OR that sets exactly the dirty bit while preserving every other bit. There is no semantic drift.

---

## 7. Implementation Correctness

- **Type compatibility:** The parameter `Hitbox_AABB *p_hitbox_aabb` is correct. The member `hitbox_aabb_flags__u8` is of type `Hitbox_Flags__u8` (`u8`), and `set_hitbox_flags_as__dirty` expects `Hitbox_Flags__u8 *`. The address-of expression `&p_hitbox_aabb->hitbox_aabb_flags__u8` yields exactly `Hitbox_Flags__u8 *`. No implicit conversions or truncation occur in this wrapper; the `|=` truncation in the callee (`u8` promoted to `unsigned int`, OR'd, truncated back to `u8`) is well-defined because the dirty bit value `2` fits within `u8` and all other bits are preserved.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (in the implementation itself), no type punning, and no out-of-bounds access. The only dereference reads and writes `p_hitbox_aabb->hitbox_aabb_flags__u8`; a null `p_hitbox_aabb` would be UB, but that is the caller's responsibility (consistent with all sibling inline flag functions such as `set_hitbox_aabb_as__not_dirty` and `is_hitbox_aabb__dirty`).
- **Validation:** No null-pointer check is performed. This is consistent with the codebase pattern — sibling functions such as `set_hitbox_aabb_as__not_dirty` (line 113) and `is_hitbox_aabb__dirty` (line 103) likewise perform no validation, so null-checking is the caller's responsibility by convention.

---

## 8. Side Effects

Mutates `p_hitbox_aabb->hitbox_aabb_flags__u8`: sets the `HITBOX_FLAG__IS_DIRTY` bit (bit 1), leaving all other flag bits (`HITBOX_FLAG__IS_ACTIVE`, etc.) unchanged.

---

## Lavender-Specific Semantics

This function is not named with "init", "initialize", or "reset" — it is a flag-setting operation, not a struct cleanup/reset. The "Initialization ≠ RAII" distinction does not apply here.
