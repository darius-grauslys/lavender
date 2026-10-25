initialize_graphics_window_manager — core/source/rendering/graphics_window_manager.c

Resets the Graphics_Window_Manager's pool to its initial (empty) conditions: it
clears every Graphics_Window slot and seeds the manager's repeatable pseudo-random
generator. (Lavender-style initialization / pool cleanup — NOT RAII resource setup.)

Pre-conditions:
1. p_graphics_window_manager must be a non-null pointer to a writable, sufficiently
   large Graphics_Window_Manager object (at least sizeof(Graphics_Window_Manager)).
2. The embedded graphics_windows array is a fixed contiguous buffer of
   MAX_QUANTITY_OF__GRAPHICS_WINDOWS (8) elements whose first member, in layout, is a
   Serialization_Header; the cast (Serialization_Header*) on it is type-safe.
3. No caller-side expectation that already-allocated windows are freed or that the
   sorted pointer array is preserved — reset is intended to clear all pool state.

Post-conditions (conditions actually guaranteed after return):
1. Every element of p_graphics_window_manager->graphics_windows is cleared: memset to 0
   then its _serialization_header is set with size_of__struct = sizeof(Graphics_Window)
   and uuid = IDENTIFIER__UNKNOWN__u32, i.e. each window reads as "unallocated".
2. p_graphics_window_manager->randomizer is seeded: seed__initial = seed__current_random
   = (Psuedo_Random_Seed__u32)(uintptr_t)p_graphics_window_manager.

Correctness Verdict: Incorrect

Semantic Alignment:
The intent (per docs/specs Section 1.4.1 Initialization and the accompanying tests) is to
reset the manager to a fully empty state. The implementation only partially achieves this.

  (a) ptr_array_of__sorted_graphic_windows is NEVER written. This array of 8
      Graphics_Window* slots is part of Graphics_Window_Manager (defines.h:2515-2516) and
      is scanned as a free-list by get_next_available_p_ptr_graphics_window_from__sorted_list
      and consulted by get_sorted_slot_of__graphics_window_from__sorted_list, which treat a
      NULL (0) slot as "free" and a non-NULL slot as "occupied". Because init does not zero
      this array, a manager that was not pre-zeroed by its caller (e.g. the test
      Graphics_Window_Manager manager; declares) retains stale/garbage pointers. Verified
      empirically: with the struct poisoned to 0xEF beforehand, all 8 sorted slots remain
      non-NULL after initialize_graphics_window_manager. The test
      graphics_window_manager__initialize__sorted_array_cleared only passes because the
      test runtime happens to zero-initialize its stack — undefined behavior to rely on.

  (b) Each Graphics_Window is zeroed by memset(0), which leaves
      graphics_window__parent__uuid == 0. However the codebase's "no parent / invalid
      identifier" sentinel for an Identifier__u32 is IDENTIFIER__UNKNOWN__u32
      (=(uint32_t)(-1), i.e. 0xFFFFFFFF) — see is_identifier_u32__invalid
      (serialization/identifiers.h:46-49) and is_graphics_window_with__parent
      (graphics_window_manager.h:115-119), which returns
      p_graphics_window && !is_identifier_u32__invalid(parent__uuid). Because 0 !=
      0xFFFFFFFF, is_graphics_window_with__parent returns TRUE for a freshly-initialized
      window. This is a direct violation of the documented "no parent after init" semantic.
      Verified empirically and deterministically: after init, gw[0].parent__uuid == 0
      and is_graphics_window_with__parent(&gw[0]) == 1. The test
      graphics_window_manager__is_graphics_window_with__parent__false_after_init fails on
      this assertion on every run.

Implementation Correctness:
  Type compatibility:
  - The cast (Serialization_Header*)p_graphics_window_manager->graphics_windows is sound:
    Graphics_Window's first member is Serialization_Header _serialization_header
    (defines.h:2483), so the address is stable and the pointer-interconvertible cast is
    well-defined.
  - sizeof(Graphics_Window) matches the size_of__struct expected by
    initialize_serialization_header__contiguous_array and is exactly what that helper
    memsets per element, so the whole Graphics_Window (including later fields such as
    parent__uuid) is zeroed.
  - (Psuedo_Random_Seed__u32)(uintptr_t)p_graphics_window_manager matches the
    seed__initial/seed__current_random field types (Psuedo_Random_Seed__u32, i.e. uint32_t).
  - MAX_QUANTITY_OF__GRAPHICS_WINDOWS is used consistently as both the iteration count and
    the array bound.
  No broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds
  access within this function.
  Undefined behavior:
  - The function itself performs no UB. However it LEAVES indeterminate/stale state in
    ptr_array_of__sorted_graphic_windows when the caller did not pre-zero the manager; any
    subsequent read of those slots (e.g. as an implicit free-list) prior to them being
    written is UB. The test relies on stack zero-initialization for safety — not guaranteed.
  - The randomizer seed truncates a pointer to 32 bits ((u32)(u64)ptr). This is
    implementation-defined but not UB, and matches the established pattern used by
    initialize_world, initialize_process_manager, initialize_aliased_texture_manager, etc.
  Validation:
  - No null-check on p_graphics_window_manager. This is consistent with the engine's
    low-level convention (cf. initialize_audio_effect, initialize_ui_context); the caller is
    responsible for the pointer. Acceptable for this role, though gfx_context.c does
    pre-zero via memset before calling.

Side Effects:
  Mutates the pointed-to Graphics_Window_Manager:
  - Overwrites all MAX_QUANTITY_OF__GRAPHICS_WINDOWS Graphics_Window slots (memset + header).
  - Writes p_graphics_window_manager->randomizer.seed__initial and
    .seed__current_random.
  - Does NOT write p_graphics_window_manager->ptr_array_of__sorted_graphic_windows
    (8 pointer slots left exactly as the caller provided them — see Verdict).
  Allocates nothing; performs no I/O.

Note (Lavender semantics): The name "initialize" here is Lavender-style initialization —
resetting a pool struct to default/empty conditions, not RAII resource acquisition. The
function correctly resets the window pool and seeds the randomizer without acquiring
resources. The defects above are about the reset being INCOMPLETE, not about it being
RAII-style.
