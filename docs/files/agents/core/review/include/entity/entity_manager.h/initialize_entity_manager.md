initialize_entity_manager — core/source/entity/entity_manager.c, lines 42-67

Zeros the Entity_Manager, initializes all entity-pool serialization headers, seeds the internal PRNG from the manager's own address, points the next-free entity pointer at the pool head, installs the default entity initializer, and registers all entity kinds.

Pre-conditions:
1. `p_entity_manager` must be a non-null pointer to a writable, properly-aligned `Entity_Manager` object. (Checked in debug builds via `#ifndef NDEBUG`; in release builds, validation is the caller's responsibility — a null pointer triggers undefined behavior via `memset`, consistent with the codebase convention, e.g. `initialize_audio_effect`.)
2. The caller is responsible for guaranteeing that `p_entity_manager` points to at least `sizeof(Entity_Manager)` bytes of owned, writable memory.
3. `MAX_QUANTITY_OF__ENTITIES` must be defined at compile time (currently 128).
4. `f_entity_initializer__default` and `register_entities` must be linked and callable (they are external symbols).

Post-conditions:
1. The entire `Entity_Manager` struct is zeroed (`memset` to 0).
2. Each `entities[i]` (0 <= i < MAX_QUANTITY_OF__ENTITIES) has its `_serialization_header.uuid` set to `IDENTIFIER__UNKNOWN__u32` (`(uint32_t)(-1)`) and `_serialization_header.size_of__struct` set to `sizeof(Entity)`; the remainder of each `Entity` is zeroed.
3. `ptr_array_of__entities[i]` is `NULL` for all i.
4. `entity_functions` (array of `Entity_Kind__Unknown` slots) is all-zeroed (every function pointer is `NULL`, i.e. the registered table is empty).
5. `randomizer.seed__initial` and `randomizer.seed__current_random` are both set to `(u32)(uint64_t)p_entity_manager`.
6. `p_ptr_entity__next_in_ptr_array` points to `ptr_array_of__entities[0]` (the head of the free slot list).
7. `f_entity_initializer` is set to `f_entity_initializer__default`.
8. `register_entities(p_entity_manager)` has been invoked (currently a no-op stub that emits a debug warning; in a full build it would populate the `entity_functions` table).

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its intent: it performs a full setup of a freshly allocated `Entity_Manager`. The `memset` zeroes the struct (Lavender's zero-then-configure pattern), then each operational field is set up: serialization headers for every entity slot, the PRNG seed, the next-free pointer at the pool head, the default entity initializer, and entity registration. No field of `Entity_Manager` is left indeterminate — every field is either zeroed or explicitly assigned. The comment block above `f_entity_initializer__default` (lines 15-26) confirms that per-entity enable/disable handler wiring is intentionally deferred to the release/reset path (`initialize_entity` / `sanitize_entity_functions`), so the all-NULL `entity_functions` table here is by design, not an omission.

Lavender-specific note: This is a manager-construction function (not a per-entity pool-return). It follows Lavender's "zero, then configure" idiom: `memset` to zero (clean up to initial conditions), then assign the non-zero operational defaults. This is the manager-level analog of Lavender initialization rather than RAII resource acquisition.

Implementation Correctness:
- Type compatibility:
  - `(Serialization_Header*)p_entity_manager->entities`: `entities` is `Entity[]` which decays to `Entity*`; `Entity` begins with a `Serialization_Header` member at offset 0, so the first-member pointer cast is valid (C11 §6.3.2.3 / the struct-to-first-member conversion guarantee). The cast matches the established pattern already used in `entity_manager.h:75` (`get_p_entity_by__uuid_from__entity_manager`).
  - `initialize_serialization_header__contiguous_array` arguments: `Serialization_Header*`, `Quantity__u32`, `Quantity__u32`. `MAX_QUANTITY_OF__ENTITIES` (literal 128) and `sizeof(Entity)` (a `size_t`) implicitly convert to `Quantity__u32` (`uint32_t`); both values are far below `UINT32_MAX`, so no truncation occurs.
  - `initialize_repeatable_psuedo_random` arguments: `Repeatable_Psuedo_Random*`, `Psuedo_Random_Seed__u32` (`uint32_t`). The seed `(u32)(uint64_t)p_entity_manager` is an explicit, well-defined narrowing of a 64-bit pointer value to 32 bits — no undefined behavior.
  - `p_entity_manager->p_ptr_entity__next_in_ptr_array` (type `Entity**`) is assigned `p_entity_manager->ptr_array_of__entities`, which decays from `Entity*[N]` to `Entity**` — an exact type match.
  - `p_entity_manager->f_entity_initializer` (type `f_Entity_Initializer` = `void(*)(Game*,World*,Entity*)`) is assigned `f_entity_initializer__default`, whose signature matches exactly.
- Undefined behavior: none. No pointer arithmetic, no null dereference (null checked in debug; caller responsibility in release per codebase convention), no type punning, no out-of-bounds access. The first-member cast is strictly valid. `memset` operates on exactly `sizeof(Entity_Manager)` bytes of a valid struct. The serialization-header loop iterates exactly `MAX_QUANTITY_OF__ENTITIES` times with a `sizeof(Entity)` stride over the `Entity[]` array, remaining in-bounds.
- Validation: the null check is debug-only (`#ifndef NDEBUG`), consistent with the codebase convention (cf. `initialize_audio_effect` and the other manager initializers). Appropriate for a low-level manager constructor.

Side Effects:
Mutates `*p_entity_manager`:
1. Zeroes the entire `Entity_Manager` struct (`memset`).
2. Overwrites each entity slot's serialization header fields (`uuid` -> `IDENTIFIER__UNKNOWN__u32`, `size_of__struct` -> `sizeof(Entity)`).
3. Writes `randomizer.seed__initial` and `randomizer.seed__current_random`.
4. Writes `p_ptr_entity__next_in_ptr_array` and `f_entity_initializer`.
5. Calls `register_entities(p_entity_manager)` — currently a stub that emits a `debug_warning` and does nothing; in a full build it would populate `entity_functions` for each registered entity kind.
(If `p_entity_manager` is null in a debug build, `debug_error` is called and the function returns early before any mutation; this is the only non-mutation path.)
No global state is touched, no I/O is performed, and no memory is allocated.
