memcpy — core/include/platform.h

Copies n bytes from the source buffer to the destination buffer; returns the destination pointer.

Pre-conditions:
1. dest (1st param, void *) must be a non-null pointer to a writable memory region of at least n bytes.
2. src (2nd param, const void *) must be a non-null pointer to a readable memory region of at least n bytes.
3. The memory ranges [dest, dest+n) and [src, src+n) must not overlap — behavior is undefined if they do.
4. n (3rd param, unsigned long) is the count of bytes to copy; no upper bound beyond the addressable buffer size.

Post-conditions:
1. The first n bytes of src are written into dest (byte-for-byte copy).
2. Returns dest (the destination pointer).

Correctness Verdict: Correct

Semantic Alignment:
The declaration correctly captures the standard memcpy semantic intent — a byte-wise copy of n bytes from src to dest, returning dest. This is a declaration-only entry (no implementation in core; the header documents that all signatures in this file "are NOT implemented in core" and are "platform dependent", implemented by a backend such as OpenGL or nds). Since no implementation exists to inspect, alignment is evaluated against the standard memcpy contract, which the declaration matches in intent.

Implementation Correctness:
Type compatibility — The third parameter is declared as unsigned long rather than the standard size_t. On the target platform (LP64 Linux, Clang 21), size_t is unsigned long, so the two are the same type and the declaration is compatible with the <string.h> declaration. However, this deviates from the C standard signature and would produce a conflicting-types diagnostic on platforms where size_t differs from unsigned long (e.g., 32-bit targets where size_t is unsigned int, or LLP64 where size_t is unsigned long long).

  This is aggravated by a redeclaration hazard: game.h includes platform.h (line 15), so any translation unit that includes game.h and <string.h> sees two memcpy declarations. The following core source files include both and are therefore potentially conflicting:
    - core/source/world/serialization/world_directory.c (platform.h line 5, <string.h> line 13)
    - core/source/ui/ui_context.c (game.h line 5, <string.h> line 16)
    - core/source/game_action/core/input/game_action__input.c (game.h line 5, <string.h> line 11)
    - core/source/collisions/core/aabb/hitbox_aabb_manager.c (game.h line 8, <string.h> line 17)
  On the LP64 target these are benign (same type); on other targets they would be a constraint violation (C11 6.2.7).

  Caller-side compatibility is sound: every callsite passes a 32-bit unsigned quantity as the size argument (Quantity__u32 or u32, both typedef'd to uint32_t). Examples: ui_text.c:70 (size_of__text, Quantity__u32), aliased_texture.c:27 (length_of__c_str, Quantity__u32), graphics_window.c:76 (size_of__p_ui_tiles, Quantity__u32), game_action__tcp_delivery.c:108 (min__u32(...) returning u32). The implicit widening from uint32_t to unsigned long is safe — no truncation.

Missing restrict qualifiers — The standard memcpy declares both pointer parameters with restrict, which documents the non-overlap contract and enables compiler optimization. This declaration omits restrict. In C a declaration without restrict is still compatible with one that has it (qualification differences are ignored for type compatibility), so this is not a correctness bug, but it silently forfeits the optimization hint and the inline documentation of the no-overlap requirement.

Undefined behavior — The declaration itself introduces none. The overlap and buffer-size UB inherent to memcpy remains the caller's responsibility — consistent with Lavender's convention (see the initialize_audio_effect review: "No validation is needed — this is a low-level struct assignment").

Validation — No validation is appropriate in this low-level memory primitive; all validation is the caller's responsibility, matching standard memcpy semantics and Lavender's conventions.

Side Effects:
Reads the src buffer; writes n bytes into the dest buffer; returns dest. No other side effects.
