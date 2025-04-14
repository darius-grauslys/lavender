#ifndef PROCESS_H
#define PROCESS_H

#include "defines_weak.h"
#include "serialization/serialization_header.h"
#include "timer.h"
#include <defines.h>

void initialize_process(
        Process *p_process,
        Identifier__u32 uuid__u32,
        m_Process m_process_run__handler,
        void *p_process_data,
        Process_Flags__u8 process_flags__u8);

static inline
void initialize_process_as__empty_process(
        Process *p_process) {
    initialize_process(
            p_process, 
            IDENTIFIER__UNKNOWN__u32, 
            0, 0, 
            PROCESS_FLAGS__NONE);
}

static inline
void initialize_process_as__serialized_process(
        Process *p_process,
        Identifier__u32 uuid__u32,
        m_Process m_process_run__handler,
        Serialization_Request *p_serialization_request,
        Process_Flags__u8 process_flags__u8) {
    initialize_process(
            p_process, 
            uuid__u32, 
            m_process_run__handler, 
            p_serialization_request, 
            process_flags__u8
            | PROCESS_FLAG__IS_CRITICAL);
}

///
/// NOTE: be sure to release your p_process_data
/// as it will be lost following this call.
///
static inline
void complete_process(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("complete_process, p_process is null.");
        return;
    }
#endif
    p_process->the_kind_of_status__this_process_has =
        Process_Status_Kind__Complete;
    p_process->p_process_data = 0;
}

///
/// NOTE: be sure to release your p_process_data
/// as it will be lost following this call.
///
static inline
void fail_process(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("fail_process, p_process is null.");
        return;
    }
#endif
    p_process->the_kind_of_status__this_process_has =
        Process_Status_Kind__Fail;
    p_process->p_process_data = 0;
}

static inline
enum Process_Status_Kind get_process_status(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("get_process_status, p_process is null.");
        return Process_Status_Kind__Unknown;
    }
#endif
    return p_process->the_kind_of_status__this_process_has;
}

static inline
bool is_process__active(Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("is_process__active, p_process is null.");
        return false;
    }
#endif
    switch (get_process_status(p_process)) {
        case Process_Status_Kind__Busy:
        case Process_Status_Kind__Idle:
        case Process_Status_Kind__Stopping:
            return true;
        default:
            return false;
    }
}

static inline
void stop_process(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("stop_process, p_process is null.");
        return;
    }
#endif
    p_process->the_kind_of_status__this_process_has =
        Process_Status_Kind__Stopping;
}

static inline
void set_process_as__stopped(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("set_process_as__stopped, p_process is null.");
        return;
    }
#endif
    p_process->the_kind_of_status__this_process_has =
        Process_Status_Kind__Stopped;
}

static inline
bool is_process__finished(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("is_process__complete, p_process is null.");
        return false;
    }
#endif
    switch (get_process_status(p_process)) {
        default:
            return false;
        case Process_Status_Kind__Complete:
        case Process_Status_Kind__Fail:
        case Process_Status_Kind__Stopped:
            return true;
    }
}

static inline
bool is_process__enqueued(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("is_process__enqueued, p_process is null.");
        return false;
    }
#endif
    return p_process && p_process->the_kind_of_status__this_process_has
        == Process_Status_Kind__Enqueued;
}

static inline
void set_process_as__enqueued(
        Process *p_process) {
    p_process->the_kind_of_status__this_process_has =
        Process_Status_Kind__Enqueued;
}

static inline
void set_process_as__dequeued(
        Process *p_process) {
    p_process->the_kind_of_status__this_process_has =
        Process_Status_Kind__Idle;
} 

static inline
void enqueue_process(
        Process *p_process_to__enqueue,
        Process *p_process_to__enqueue_behind) {
    p_process_to__enqueue_behind->p_enqueued_process =
        p_process_to__enqueue;
    set_process_as__enqueued(
            p_process_to__enqueue);
}

static inline
bool is_process__available(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("is_process__available, p_process is null.");
        return false;
    }
#endif
    return p_process && p_process->the_kind_of_status__this_process_has
        == Process_Status_Kind__None;
}

static inline
bool does_process_have__run_handler(
        Process *p_process) {
#ifndef NDEBUG
    if (!p_process) {
        debug_abort("does_process_have__run_handler, p_process is null.");
        return false;
    }
#endif
    return p_process->m_process_run__handler;
}

static inline
void set_process__sub_state(
        Process *p_this_process,
        u8 sub_state__u8) {
    p_this_process->process_sub_state__u8 = sub_state__u8;
}

static inline
i32F20 get_process__runtime(Process *p_process) {
    return p_process->process_runtime__i32F20;
}

static inline
i32 get_process_runtime_in__ticks(Process *p_process) {
    return p_process->process_runtime__i32F20 >> 14;
}

static inline
bool is_process__critical(Process *p_process) {
    return p_process->process_flags__u8
         & PROCESS_FLAG__IS_CRITICAL
         ;
}

static inline
void set_process_as__critical(Process *p_process) {
    p_process->process_flags__u8 |=
        PROCESS_FLAG__IS_CRITICAL
        ;
}

static inline
void set_process_as__NOT_critical(Process *p_process) {
    p_process->process_flags__u8 &=
        ~PROCESS_FLAG__IS_CRITICAL
        ;
}

static inline
bool is_process__sub_process(Process *p_process) {
    return p_process->process_flags__u8
         & PROCESS_FLAG__IS_SUB_PROCESS
         ;
}

static inline
void set_process_as__sub_process(Process *p_process) {
    p_process->process_flags__u8 |=
        PROCESS_FLAG__IS_SUB_PROCESS
        ;
}

static inline
void set_process_as__NOT_sub_process(Process *p_process) {
    p_process->process_flags__u8 &=
        ~PROCESS_FLAG__IS_SUB_PROCESS
        ;
}

static inline
Process_Kind get_the_kind_of__process(
        Process *p_process) {
    return p_process->the_kind_of__process_this__process_is;
}

static inline
void set_the_kind_of__process(
        Process *p_process,
        Process_Kind the_kind_of__process) {
    p_process->the_kind_of__process_this__process_is =
        the_kind_of__process;
}

#endif
