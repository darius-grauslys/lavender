#include <timer.h>

bool progress_timer__guard_restart__u32(
        Timer__u32 *p_timer__u32,
        Quantity__u32 quantity_of__ticks__u32,
        bool is_restarting) {
    if (quantity_of__ticks__u32
> p_timer__u32->remaining__u32) {
        quantity_of__ticks__u32 -=
            p_timer__u32->remaining__u32;
        if (quantity_of__ticks__u32
                > p_timer__u32->start__u32) {
            quantity_of__ticks__u32 %=
                p_timer__u32->start__u32;
        }
        if (is_restarting) {
            reset_timer_u32(p_timer__u32);
            p_timer__u32->remaining__u32 -= quantity_of__ticks__u32;
        } else {
            p_timer__u32->remaining__u32 = 0;
        }
        return true;
    }
    p_timer__u32->remaining__u32 -= quantity_of__ticks__u32;
    return false;
}

bool progress_timer__guard_restart__u16(
        Timer__u16 *p_timer__u16,
        Quantity__u16 quantity_of__ticks__u16,
        bool is_restarting) {
    if (quantity_of__ticks__u16
> p_timer__u16->remaining__u16) {
        quantity_of__ticks__u16 -=
            p_timer__u16->remaining__u16;
        if (quantity_of__ticks__u16
                > p_timer__u16->start__u16) {
            quantity_of__ticks__u16 %=
                p_timer__u16->start__u16;
        }
        reset_timer_u16(p_timer__u16);
        p_timer__u16->remaining__u16 -= quantity_of__ticks__u16;
        return true;
    }
    p_timer__u16->remaining__u16 -= quantity_of__ticks__u16;
    return false;
}
