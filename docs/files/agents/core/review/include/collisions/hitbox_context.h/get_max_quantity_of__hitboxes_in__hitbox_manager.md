get_max_quantity_of__hitboxes_in__hitbox_manager — core/source/collisions/hitbox_context.c

Public accessor that finds a hitbox manager instance by UUID and returns the max quantity of hitboxes in that manager's pool.

Pre-conditions:
1. p_hitbox_context must be a non-null pointer to an initialized Hitbox_Context.
2. uuid_of__hitbox_manager__u32 must not be IDENTIFIER__UNKNOWN__u32 (enforced internally).

Post-conditions:
1. On success: returns the Quantity__u32 max hitbox count for the found manager.
2. On failure (instance not found or invalid): returns 0. Debug error and warning messages are logged.

Correctness Verdict: Correct

Semantic Alignment: The function correctly fulfills the intent of looking up a manager by UUID and returning its max hitbox quantity. It delegates to get_p_hitbox_manager_instance_using__uuid_from__hitbox_context for the lookup and get_max_quantity_of__hitboxes_in__this_hitbox_manager for the field read.

Implementation Correctness:
Type compatibility — all types are correct. Quantity__u32 return type matches the field read. The delegation to the static inline helper is type-correct.
Undefined behavior — no pointer arithmetic, no null dereference. Uses is_p_hitbox_manager_instance__valid (which checks non-null, valid uuid, and non-null pVM_hitbox_manager) before accessing the manager, preventing null dereference.
Validation — uses is_p_hitbox_manager_instance__valid, the strongest validation available, which is more thorough than the simple NULL checks used in some sibling functions. Note: the function calls both debug_warning("Returning 0 here.") and debug_error(...) on failure, which is redundant — both are emitted. This appears to be a leftover debugging artifact. It does not affect correctness.

Side Effects:
No side effects. The function is a pure lookup. Logs debug messages on failure.
