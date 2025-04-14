#include "time/no_gui_time.h"
#include "numerics.h"
#include "timer.h"
#include "no_gui_numerics.h"

#ifdef _WIN32

void NO_GUI_initialize_time(void) {
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

struct timespec _NO_GUI_timespec__initial;

void NO_GUI_initialize_time(void) {
    clock_gettime(
            CLOCK_MONOTONIC, 
            &_NO_GUI_timespec__initial);
}

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

    if (timespec__current.tv_nsec < _NO_GUI_timespec__initial.tv_nsec) {
        timespec__current.tv_sec--;
        timespec__current.tv_nsec = 
            _NO_GUI_timespec__initial.tv_nsec
            - timespec__current.tv_nsec;
    } else {
        timespec__current.tv_nsec -= _NO_GUI_timespec__initial.tv_nsec;
    }
    timespec__current.tv_sec = _NO_GUI_timespec__initial.tv_sec;

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

void PLATFORM_get_date_time(Date_Time *p_date_time) {
    time_t time_raw;
    struct tm * p_time_local;

    time(&time_raw);
    p_time_local = localtime(&time_raw);

    p_date_time->seconds =
        p_time_local->tm_sec;
    p_date_time->minutes =
        p_time_local->tm_min;
    p_date_time->hours =
        p_time_local->tm_hour;
    p_date_time->days =
        p_time_local->tm_mday;
    p_date_time->months =
        p_time_local->tm_mon;
    p_date_time->years =
        p_time_local->tm_year;
}

#endif
