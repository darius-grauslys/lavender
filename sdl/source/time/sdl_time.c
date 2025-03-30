#include "time/sdl_time.h"
#include "numerics.h"
#include "timer.h"
#include "sdl_numerics.h"
#include <SDL2/SDL_timer.h>

#ifdef _WIN32

void SDL_initialize_time(void) {
    return;
}

///
/// NOTE: Timer value is considered to be u32F20 seconds
///
#include <windows.h>
#include <mmsystem.h>
u32F20 PLATFORM_get_time_elapsed(
        Timer__u32 *p_timer__seconds__u32,
        Timer__u32 *p_timer__nanoseconds__u32) {
    DWORD time__old = get_time_elapsed_from__timer_u32(
            p_timer__nanoseconds__u32);
    DWORD time__current = timeGetTime();

    if (time__old == time__current)
        return 0;

    u32 elapsed__miliseconds = 
        subtract_u32__no_overflow(
                time__current,
                time__old);
    if (!elapsed__miliseconds) {
        elapsed__miliseconds =
            time__current
            + (((uint32_t)-1)
                - time__old)
            ;
    }
    
    (void)progress_timer__u32(
                p_timer__nanoseconds__u32, 
                elapsed__miliseconds);

    return 
        ((elapsed__miliseconds
                & MASK(10))
                << 10)
        ;
}
#else
#include <time.h>

uint32_t _SDL_miliseconds_last = 0;

void SDL_initialize_time(void) {
    _SDL_miliseconds_last =
        SDL_GetTicks();
}

u32F20 PLATFORM_get_time_elapsed(
        Timer__u32 *p_timer__seconds__u32,
        Timer__u32 *p_timer__nanoseconds__u32) {
    // TODO: maybe leverage a 32 bit version
    uint32_t total_miliseconds = SDL_GetTicks();

    (void)progress_timer__u32(
            p_timer__seconds__u32,
            total_miliseconds / 1000);

    (void)progress_timer__u32(
            p_timer__nanoseconds__u32,
            (total_miliseconds % 1000) * 1000000);

    uint32_t elapsed_miliseconds =
        total_miliseconds
        - _SDL_miliseconds_last;
    _SDL_miliseconds_last = total_miliseconds;
    return elapsed_miliseconds << 10;
}
/*
///
/// NOTE: Timer value is considered to be u32F20 seconds
///
u32F20 PLATFORM_get_time_elapsed(
        Timer__u32 *p_timer__seconds__u32,
        Timer__u32 *p_timer__nanoseconds__u32) {
    struct timespec timespec__current;
    clock_gettime(
            CLOCK_MONOTONIC, 
            &timespec__current);

    if (timespec__current.tv_nsec < _SDL_timespec__begin.tv_nsec) {
        timespec__current.tv_sec -= _SDL_timespec__begin.tv_sec - 1;
        timespec__current.tv_nsec = 
            _SDL_timespec__begin.tv_nsec
            - timespec__current.tv_nsec;
    } else {
        timespec__current.tv_sec -= _SDL_timespec__begin.tv_sec;
        timespec__current.tv_nsec -= _SDL_timespec__begin.tv_nsec;
    }

    u32 elapsed__seconds = 
        subtract_u32__no_overflow(
                timespec__current.tv_sec, 
                get_time_elapsed_from__timer_u32(
                    p_timer__seconds__u32));
    if (!elapsed__seconds) {
        elapsed__seconds=
            timespec__current.tv_sec
            + p_timer__seconds__u32->remaining__u32
            ;
    }

    u32 elapsed__nanoseconds =
        subtract_u32__no_overflow(
                timespec__current.tv_nsec, 
                get_time_elapsed_from__timer_u32(
                    p_timer__nanoseconds__u32));
    if (!elapsed__nanoseconds) {
        elapsed__nanoseconds=
            timespec__current.tv_nsec
            + p_timer__nanoseconds__u32->remaining__u32
            ;
    }

    (void)progress_timer__u32(
                p_timer__seconds__u32, 
                elapsed__seconds);
    if (progress_timer__u32(
                p_timer__nanoseconds__u32, 
                elapsed__nanoseconds)) {
        elapsed__seconds--;
    }

    return 
        (elapsed__seconds << 20)
        + ((elapsed__nanoseconds
                & MASK(30))
                >> 10)
        ;
}
*/
#endif
