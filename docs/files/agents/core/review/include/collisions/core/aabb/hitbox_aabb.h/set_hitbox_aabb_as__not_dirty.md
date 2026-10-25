# set_hitbox_aabb_as__not_dirty

- **Function name:** `set_hitbox_aabb_as__not_dirty`
- **File of origin:** `core/include/collisions/core/aabb/hitbox_aabb.h` (lines 113-116)

---

## 2. Semantic

Clears the `HITBOX_FLAG__IS_DIRTY` bit in a `Hitbox_AABB`'s `hitbox_aabb_flags__u8` field, marking the hitbox as "not dirty" (i.e., its collision state is clean and does not require re-computation).

```c
static inline
bool set_hitbox_aabb_as__not_dirty(Hitbox_AABB *p_hitbox_aabb) {
    return set_hitbox_flags_as__not_dirty(&p_hitbox_aabb->hitbox_aabb_flags__u8);
}
```

This is a thin wrapper that delegates to `set_hitbox_flags_as__not_dirty(Hitbox_Flags__u8 *p_hitbox_flags__u8)` in `core/include/collisions/hitbox.h` (lines 19-24):

```c
static inline
bool set_hitbox_flags_as__not_dirty(Hitbox_Flags__u8 *p_hitbox_flags__u8) {
    return *p_hitbox_flags__u8 &=
        ~HITBOX_FLAG__IS_DIRTY
        ;
}
```

Where `Hitbox_Flags__u8` is `u8` (`defines.h:329`) and `HITBOX_FLAG__IS_DIRTY` is `BIT(1)` (`defines.h:332`). The compound assignment `&=` evaluates to the new value stored, so the function returns the full flag byte after the dirty bit has been cleared.

---

## 3. Pre-conditions

1. `p_hitbox_aabb` must be a non-null pointer to a valid, initialized `Hitbox_AABB` struct (`defines.h:450-458`).
2. The `hitbox_aabb_flags__u8` field of the struct must be a readable and writable `Hitbox_Flags__u8` (`u8`).

---

## 4. Post-conditions

1. The `HITBOX_FLAG__IS_DIRTY` bit in `p_hitbox_aabb->hitbox_aabb_flags__u8` is cleared (set to 0); all other flag bits are unchanged.
2. Returns the new value of `p_hitbox_aabb->hitbox_aabb_flags__u8` (a `bool` — nonzero if any other flag bit remains set, zero if all flags are now clear).

---

## 5. Correctness Verdict

**Correct.**

---

## 6. Semantic Alignment

The implementation fulfills the semantic intent: it clears the dirty flag on a hitbox AABB so the collision system knows its state is up-to-date. The delegation chain `set_hitbox_aabb_as__not_dirty` → `set_hitbox_flags_as__not_dirty` → `*p_hitbox_flags__u8 &= ~HITBOX_FLAG__IS_DIRTY` correctly performs a bitwise-AND with the complement of the dirty flag, preserving all other bits while clearing only `HITBOX_FLAG__IS_DIRTY`. There is no semantic drift.

---

## 7. Implementation Correctness

- **Type compatibility:** The parameter `Hitbox_AABB *p_hitbox_aabb` is correct. The member `hitbox__aabb_flags__u8` is of type `Hitbox_Flags__u8` (`u8`), and `set_hitbox_flags_as__not_dirty` expects `Hitbox_Flags__u8 *`. The address-of expression `&p_hitbox_aabb->hitbox_aabb_flags__u8` yields exactly `Hitbox_Flags__u8 *`. No implicit conversions or truncation occur.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (in the implementation itself), no type punning, and no out-of-bounds access. The `&=` / `~HITBOX_FLAG__IS_DIRTY` operation operates on a `u8` value and is well-defined.
- **Validation:** No null-pointer check is performed. This is consistent with the codebase pattern — sibling functions such as `set_hitbox_aabb_as__dirty` (line 108) and `is_hitbox_aabb__dirty` (line 103) likewise perform no validation, so null-checking is the caller's responsibility by convention.

---

## 8. Side Effects

Mutates `p_hitbox_aabb->hitbox_aabb_flags__u8`: clears the `HITBOX_FLAG__IS_DIRTY` bit (bit 1), leaving all other flag bits (`HITBOX_FLAG__IS_ACTIVE`, etc.) unchanged.

---

## Lavender-Specific Semantics

This function is not named with "init", "initialize", or "reset" — it is a flag-clearing operation, not a struct cleanup/reset. The "Initialization ≠ RAII" distinction does not apply here.
