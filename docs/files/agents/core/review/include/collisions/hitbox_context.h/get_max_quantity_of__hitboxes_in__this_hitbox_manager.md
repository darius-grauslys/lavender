get_max_quantity_of__hitboxes_in__this_hitbox_manager — core/source/collisions/hitbox_context.c

Static inline helper that reads the quantity_of__hitboxes field directly from the first 32 bits of a hitbox manager pool, relying on the Hitbox_Manager_Intrinsic layout contract.

Pre-conditions:
1. pM_hitbox_manager must be a non-null pointer to a valid hitbox manager pool that obeys the Hitbox_Manager_Intrinsic layout (first 32 bits must be a Quantity__u32 quantity_of__hitboxes field).

Post-conditions:
1. Returns the Quantity__u32 value of the first 32 bits of the hitbox manager pool, which represents the maximum number of hitboxes in that pool.

Correctness Verdict: Correct

Semantic Alignment: The function correctly fulfills the intent of reading the max hitbox quantity from a manager. The direct memory read of the first 32 bits matches the Hitbox_Manager_Intrinsic struct where quantity_of__hitboxes is the first (and first 32-bit) field.

Implementation Correctness:
Type compatibility — pM_hitbox_manager (void*) is cast to Quantity__u32* and dereferenced. The return type is Quantity__u32, matching the dereferenced value type.
Undefined behavior — relies on the documented contract that ALL hitbox managers obey Hitbox_Manager_Intrinsic. If this contract is violated, the read would be UB. Within the contract, the read is well-defined. No explicit NULL check is performed — this is acceptable because the function is static inline and only called from internal code that validates the manager pointer beforehand.
Validation — no validation is needed for an internal static helper; callers are responsible for passing valid pointers.

Side Effects:
No side effects. The function is a pure read of the first 32 bits of the manager pool.
