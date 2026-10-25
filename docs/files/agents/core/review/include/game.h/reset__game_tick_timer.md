reset__game_tick_timer — core/source/game.c

Resets the game tick timer by carrying the fractional remainder of accumulated time into the tick accumulator and zeroing the elapsed-time counter.

Pre-conditions:
1. p_game must be a non-null pointer to a writable Game object.
2. p_game->tick_accumilator__u32F20 and p_game->time_elapsed__u32F20 are valid u32F20 values (uint32_t).

Post-conditions:
1. p_game->time_elapsed__u32F20 is set to 0.
2. p_game->tick_accumilator__u32F20 is intended to retain only the fractional remainder of (accumulator + elapsed) below the 15-bit tick boundary.

Correctness Verdict: Incorrect

Semantic Alignment:
The intent of reset__game_tick_timer is to extract whole ticks from the combined accumulator and elapsed time, then preserve the fractional remainder in tick_accumilator__u32F20. The correct computation would be:

    p_game->tick_accumilator__u32F20 =
        (p_game->tick_accumilator__u32F20
         + p_game->time_elapsed__u32F20)
        & MASK(15);

The actual implementation instead subtracts the whole-tick portion from the original accumulator:

    p_game->tick_accumilator__u32F20 -=
        (p_game->tick_accumilator__u32F20
         + p_game->time_elapsed__u32F20)
        & ~MASK(15);

This is semantically wrong in two ways:

1. Fractional remainder is lost when no whole ticks have elapsed. When (A + T) < 2^15, the mask ~MASK(15) yields 0, so the accumulator is unchanged and the fractional contribution from T is discarded. For example, with A=0 and T=0x4000, the correct remainder is 0x4000 but the code leaves the accumulator at 0.

2. Unsigned integer underflow occurs when whole ticks have elapsed and the accumulator is smaller than the whole-tick portion. For example:
   - A=0, T=0x8000: result = 0 - 0x8000 = 0xFFFF8000 (underflow; should be 0)
   - A=0x4000, T=0x8000: result = 0x4000 - 0x8000 = 0xFFFFC000 (underflow; should be 0x4000)

The implementation does not fulfill the semantic intent of preserving the fractional remainder of accumulated time.

Implementation Correctness:
Type compatibility — all fields are u32F20 (uint32_t), and MASK(15) evaluates to ((u32)BIT(15) - 1) = 0x7FFF, so ~MASK(15) = 0xFFFF8000. The arithmetic is type-consistent.
Undefined behavior — the subtraction is performed on unsigned integers, so underflow wraps around (defined behavior in C for unsigned types), but the resulting value is semantically incorrect and corrupts the accumulator.
Validation — no validation is needed; this is a low-level timer reset function. The caller is responsible for ensuring p_game is valid.

Side Effects:
Mutates p_game->tick_accumilator__u32F20 and p_game->time_elapsed__u32F20. No other observable side effects.
