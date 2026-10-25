# Function Review: register_hitbox_managers

- **Function name:** `register_hitbox_managers`
- **File of origin:** `core/source/collisions/implemented/hitbox_context/hitbox_manager_registrar.c` (lines 7–32)

---

## 2. Semantic

Registers the Hitbox_AABB_Manager with the Hitbox_Context by delegating to `register_hitbox_manager`, supplying the AABB allocator, deallocator, opaque property access handler, and the component metadata (sizes, quantities, fractional precision) that describe the AABB hitbox's fixed-point data layout.

---

## 3. Pre-conditions

1. `p_hitbox_context` must be non-null and a valid pointer. (Not checked by this function.)
2. `p_hitbox_context->hitbox_manager_registration_records[]` and `p_hitbox_context->hitbox_manager_instance__invocation_table[]` arrays must be accessible (they are static array members of `Hitbox_Context`, so they are available as long as the pointer is valid).
3. The AABB function pointers (`f_hitbox_manager__allocator_AABB`, `f_hitbox_manager__deallocator_AABB`, `f_hitbox_manager__opaque_property_access_of__hitbox_AABB`) must be declared with signatures compatible with their respective typedefs.

---

## 4. Post-conditions

1. `p_hitbox_context->hitbox_manager_registration_records[Hitbox_Manager_Type__AABB]` is populated with:
   - `size_of__components__dimensions` = `sizeof(i32)` = 4
   - `size_of__components__pos_vel` = `sizeof(i32F4)` = 4
   - `size_of__components__acceleration` = `sizeof(i16F8)` = 2
   - `quantity_of__components__dimensions` = 2
   - `quantity_of__components__pos_vel_acc` = 3
   - `fractional_percision_of__dimensions` = 0
   - `fractional_percision_of__pos_vel` = 4
   - `fractional_percision_of__acceleration` = **16** — see Semantic Alignment note
2. `p_hitbox_context->hitbox_manager_instance__invocation_table[Hitbox_Manager_Type__AABB]` is populated with the three AABB function pointers.
3. No resources are allocated (no RAII).
4. The function returns `void`.

---

## 5. Correctness Verdict

**Incorrect**

A semantic bug exists in the fractional precision registration for acceleration components. See **6. Semantic Alignment**.

---

## 6. Semantic Alignment

The function's intent is to register the AABB hitbox manager with correct component metadata.

**Correctly passed:**

| Parameter | Value | Type / Meaning |
|---|---|---|
| Allocator fn ptr | `f_hitbox_manager__allocator_AABB` | Matches `f_Hitbox_Manager__Allocator` typedef exactly — signature verified |
| Deallocator fn ptr | `f_hitbox_manager__deallocator_AABB` | Matches `f_Hitbox_Manager__Deallocator` typedef exactly — signature verified |
| Opaque access fn ptr | `f_hitbox_manager__opaque_property_access_of__hitbox_AABB` | Matches `f_Hitbox_Manager__Opaque_Property_Access_Of__Hitbox` typedef exactly — signature verified |
| Manager type | `Hitbox_Manager_Type__AABB` (= `Hitbox_Manager_Type__Default` = 0) | Passes debug validation (`>= Hitbox_Manager_Type__Unknown` = 2) in `register_hitbox_manager` |
| `size_of__components__dimensions` | `sizeof(i32)` = 4 | `i32` is `int32_t`, 4 bytes — correct |
| `size_of__components__pos_vel` | `sizeof(i32F4)` = 4 | `i32F4` is `int32_t`, 4 bytes — correct |
| `size_of__components__acceleration` | `sizeof(i16F8)` = 2 | `i16F8` is `int16_t`, 2 bytes — correct |
| `quantity_of__components__dimensions` | 2 | Width + height — consistent with `Quantity__u32 width/height` fields in `Hitbox_AABB` |
| `quantity_of__components__pos_vel_acc` | 3 | X, Y, Z — consistent with `Vector__3i32F4`/`Vector__3i16F8` being 3-component vectors |
| `fractional_percision_of__dimensions` | `FRACTIONAL_PERCISION_0__BIT_SIZE` = 0 | `i32` has 0 fractional bits — correct |
| `fractional_percision_of__pos_vel` | `FRACTIONAL_PERCISION_4__BIT_SIZE` = 4 | `i32F4` has 4 fractional bits — correct |
| `fractional_percision_of__acceleration` | `FRACTIONAL_PERCISION_16__BIT_SIZE` = 16 | **BUG** — see below |

**Bug — Incorrect fractional precision for acceleration:**

The type `i16F8` is defined as `int16_t` (2 bytes) with **8 fractional bits** (the "F8" in the naming convention, matching the pattern `i32F4` = int32_t with 4 fractional bits). The function registers the fractional precision as `FRACTIONAL_PERCISION_16__BIT_SIZE` (value 16), which is incorrect — it should be `FRACTIONAL_PERCISION_8__BIT_SIZE` (value 8).

The correct macro `FRACTIONAL_PERCISION_8__BIT_SIZE` (defined at `defines.h:49`) exists and is available, but the wrong macro is used. This causes `Hitbox_Context` to record that acceleration components have 16 bits of fractional precision when they actually have 8. Any downstream code that reads `fractional_percision_of__acceleration` from the registration record to interpret or convert acceleration values will produce incorrect results (e.g., scaling values by 2^16 instead of 2^8).

---

## 7. Implementation Correctness

- **Type compatibility:** The three function pointer arguments match their target typedefs exactly — no implicit conversions. ✓
- **Implicit conversions:** The `SIZE_OF__HITBOX_COMPONENTS` macro wraps `sizeof()` expressions, which return `size_t`. These are implicitly narrowed to `u8` for the `size_of__components__*` parameters. The values (4, 4, 2) fit within `u8` range (0–255), so no truncation occurs for the current type set. This should be noted as a latent risk if types ever exceed 255 bytes, but is safe for current usage.
- **Undefined behavior:** No null dereference (assuming pre-condition holds), no out-of-bounds access (enum index 0 is valid for arrays of size `Hitbox_Manager_Type__Unknown` = 2), no broken pointer arithmetic, no type punning. ✓
- **Validation:** No null check on `p_hitbox_context`. Given the function's role as a thin registration helper called exclusively from `initialize_hitbox_context` (which itself is expected to be called with a valid, already-allocated context), the absence of a null check is a minor concern. The function does emit debug warnings, suggesting runtime state awareness, but does not guard against a null context pointer. This is acceptable as caller responsibility given the Lavender codebase pattern where setup functions assume valid inputs, though a defensive null guard would be more robust.
- **Argument/Parameter mapping:** All 13 arguments map correctly to the 13 parameters of `register_hitbox_manager` in the correct order. The macro "description" labels (`dimensions`, `pos_vel`, `acceleration`) are documentation-only and have no semantic effect on the expanded values. ✓

---

## 8. Side Effects

- Emits two `debug_warning` calls with informational messages (lines 8–9).
- Mutates `p_hitbox_context->hitbox_manager_registration_records[Hitbox_Manager_Type__AABB]`, populating all 8 metadata fields.
- Mutates `p_hitbox_context->hitbox_manager_instance__invocation_table[Hitbox_Manager_Type__AABB]`, populating 3 function pointer fields.
- No memory allocation, no RAII, no I/O, no global state mutation.

---

## Lavender-Specific Semantics

- **Initialization ≠ RAII:** The function name contains "register" (not "init"/"initialize"/"reset"), so this distinction does not strictly apply. However, the function is NOT performing resource acquisition — it populates existing arrays within the `Hitbox_Context` struct. This is consistent with Lavender's non-RAII pattern, where registration and setup do not couple with resource allocation.
- The function does not call any allocation functions (`malloc`, etc.). It only writes metadata and function pointers into pre-existing struct arrays. This aligns with the Lavender engine's pool-based, non-RAII approach where "initialization" means clearing/resetting structs to default state, and registration means associating function pointers and metadata with a manager type in a pre-allocated context.
