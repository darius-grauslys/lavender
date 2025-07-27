#include "process/process_table.h"
#include "defines_weak.h"
#include "process/process.h"
#include "process/process_priority_table_entry.h"
#include "defines.h"

static inline
Process_Priority_Table_Entry *get_p_process_priority_table_entry_by__priority(
        Process_Table *p_process_table,
        uint8_t process_priority) {
    if (process_priority >= PROCESS_MAX_PRIORITY_LEVEL) {
        return p_process_table->process_priority_table;
    }
    return &p_process_table->process_priority_table[process_priority];
}

Process_Priority_Table_Entry
*get_lowest_used_p_process_priorty_table_entry(
        Process_Table *p_process_table,
        uint32_t priority_levels_beneath__this_one) {
    if (!priority_levels_beneath__this_one) {
        return 0;
    }
    for (Index__u32 priority_level = priority_levels_beneath__this_one - 1;
            priority_level > 0;
            priority_level--) {
        Process_Priority_Table_Entry *p_process_priority_table_entry =
            get_p_process_priority_table_entry_by__priority(
                    p_process_table, 
                    priority_level);
        if (!is_process_priority_table_entry__empty(
                    p_process_priority_table_entry)) {
            return p_process_priority_table_entry;
        }
    }

    return 0;
}


void initialize_process_table(
        Process_Table *p_process_table) {
    memset(p_process_table,
            0,
            sizeof(Process_Table));
    p_process_table->p_process_priority_table_entry__current =
        p_process_table->process_priority_table;
}

bool add_process_to__process_table(
        Process_Table *p_process_table,
        Process *p_process) {
    Process_Priority__u8 process_priority_of__added_process =
        get_process_priorty_of__process(p_process);

    Process_Priority_Table_Entry *p_process_priority_table_entry = 0;
    for (Process_Priority__u8 process_priority =
            PROCESS_MAX_PRIORITY_LEVEL - 1;
            process_priority > process_priority_of__added_process;
            process_priority--) {
        p_process_priority_table_entry =
            get_p_process_priority_table_entry_by__priority(
                    p_process_table, 
                    process_priority);
        if (is_process_priority_table_entry__empty(
                    p_process_priority_table_entry)) {
            continue;
        }
        if (!move_process_priorty_table_entry_up__one_in__ptr_array_of__processes
                (p_process_table,
                 p_process_priority_table_entry)) {
            return false;
        }
    }
    p_process_priority_table_entry =
        get_p_process_priority_table_entry_by__priority(
                p_process_table, 
                get_process_priorty_of__process(p_process));
    if (!p_process_priority_table_entry) {
        return false;
    }
    if (is_process_priority_table_entry__empty(
                p_process_priority_table_entry)) {
        Process_Priority_Table_Entry *p_process_priority_table_entry__next_priority =
            get_lowest_used_p_process_priorty_table_entry(
                    p_process_table, 
                    process_priority_of__added_process);
        initialize_process_priority_table_entry(
                p_process_priority_table_entry, 
                (p_process_priority_table_entry__next_priority
                 != 0)
                ? p_process_priority_table_entry__next_priority->p_ptr_process__oldest_of__priority+1
                : p_process_table->ptr_array_of__processes);
        return true;
    }
    
    add_process_to__process_priorty_table_entry_in__ptr_array_of__processes(
            p_process_table,
            p_process_priority_table_entry,
            p_process);

    return true;
}

void remove_process_from__process_table(
        Process_Table *p_process_table,
        Process *p_process) {
    Process_Priority__u8 process_priority_of__removed_process =
        get_process_priorty_of__process(p_process);

    Process_Priority_Table_Entry *p_process_priority_table_entry =
        get_p_process_priority_table_entry_by__priority(
                p_process_table, 
                process_priority_of__removed_process);
    if (!remove_process_from__process_priority_table_entry_from__ptr_array_of__processes(
            p_process_priority_table_entry,
            p_process)) {
        debug_error("remove_process_from__process_table, process not found under it's own priority_level");
        return;
    }

    for (Process_Priority__u8 process_priority = process_priority_of__removed_process+1;
            process_priority < PROCESS_MAX_PRIORITY_LEVEL;
            process_priority++) {
        p_process_priority_table_entry =
            get_p_process_priority_table_entry_by__priority(
                    p_process_table, 
                    process_priority);
        move_process_priorty_table_entry_down__one_in__ptr_array_of__processes(
                p_process_table,
                p_process_priority_table_entry);
    }
}

void begin_polling_of__process_table(
        Process_Table *p_process_table) {
    p_process_table->p_process_priority_table_entry__current =
        p_process_table->process_priority_table;
}

Process *poll_next_p_process_from__process_table(
        Process_Table *p_process_table) {
    Process *p_process = 0;
    for (Process_Priority__u8 process_priority = 0;
            process_priority < PROCESS_MAX_PRIORITY_LEVEL;
            process_priority++) {
        if (poll_next_p_process_from__process_priority_table_entry(
                    p_process_table->p_process_priority_table_entry__current,
                    &p_process)) {
            if (++p_process_table->p_process_priority_table_entry__current
                    >= &p_process_table->process_priority_table[PROCESS_MAX_PRIORITY_LEVEL]) {
                p_process_table->p_process_priority_table_entry__current =
                    p_process_table->process_priority_table;
                return 0; // all processes have been polled.
            }
            continue;
        }
        break;
    }
    return p_process;
}

Quantity__u32 get_quantity_of__processes_in__process_table(
        Process_Table *p_process_table) {
    Quantity__u32 quantity_of__processes = 0;
    for (Index__u32 index_of__priority_table = 0;
            index_of__priority_table < PROCESS_MAX_PRIORITY_LEVEL;
            index_of__priority_table++) {
        Process_Priority_Table_Entry *p_process_priority_table_entry =
            get_p_process_priority_table_entry_by__priority(
                    p_process_table, 
                    index_of__priority_table);
        quantity_of__processes += 
            get_quantity_of__processes_in__process_priority_table_entry(
                    p_process_priority_table_entry);
    }
    return quantity_of__processes;
}
