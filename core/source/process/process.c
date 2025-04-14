#include "defines.h"
#include "defines_weak.h"
#include "serialization/serialization_header.h"
#include "timer.h"
#include <process/process.h>
#include <string.h>

void initialize_process(
        Process *p_process,
        Identifier__u32 uuid__u32,
        m_Process m_process_run__handler,
        void *p_process_data,
        Process_Flags__u8 process_flags__u8) {
    memset(p_process, 0, sizeof(Process));
    initialize_serialization_header(
            &p_process->_serialization_header, 
            uuid__u32, 
            sizeof(Process));
    p_process->m_process_run__handler =
        m_process_run__handler;
    p_process->process_runtime__i32F20 = 0;
    p_process->the_kind_of__process_this__process_is =
        Process_Kind__None;
    p_process->the_kind_of_status__this_process_has =
        Process_Status_Kind__None;
    p_process->p_process_data =
        p_process_data;
    p_process->process_sub_state__u8 = 0;
    p_process->process_flags__u8 = process_flags__u8;
}
