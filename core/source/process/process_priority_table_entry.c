#include "process/process_priority_table_entry.h"
#include "defines.h"

void initialize_process_priority_table_entry(
        Process_Priority_Table_Entry *p_process_priority_table_entry,
        Process **p_ptr_process__first) {
    p_process_priority_table_entry->p_ptr_process__current_priority_to__swap =
        p_ptr_process__first;
    p_process_priority_table_entry->p_ptr_process__oldest_of__priority =
        p_ptr_process__first;
    p_process_priority_table_entry->p_ptr_process__youngest_of__priority =
        p_ptr_process__first;
}

///
/// So long as the process priority table entry is NOT empty
/// this will move the pointer delimiters of the entry up by one.
///
/// NOTE: The non-empty process priority table entries of HIGHER priority
/// MUST be moved PRIOR.
///
/// Returns false if movement fails.
///
bool move_process_priorty_table_entry_up__one_in__ptr_array_of__processes(
        Process_Table *p_process_table,
        Process_Priority_Table_Entry *p_process_priority_table_entry) {
    if (is_process_priority_table_entry__empty(
                p_process_priority_table_entry)) {
        return true;
    }
    if (p_process_priority_table_entry->p_ptr_process__oldest_of__priority + 1
            > &p_process_table->ptr_array_of__processes[
            PROCESS_MAX_QUANTITY_OF-1]) {
        return false;
    }

    *++p_process_priority_table_entry->p_ptr_process__oldest_of__priority =
        *p_process_priority_table_entry->p_ptr_process__youngest_of__priority;
    *p_process_priority_table_entry->p_ptr_process__youngest_of__priority = 0;

    return true;
}

///
/// So long as the process priority table entry is NOT empty
/// this will move the pointer delimiters of the entry down by one.
///
/// NOTE: The non-empty process priority table entries of HIGHER priority
/// MUST be moved AFTERWARDS.
///
/// Returns false if movement fails.
///
bool move_process_priorty_table_entry_down__one_in__ptr_array_of__processes(
        Process_Table *p_process_table,
        Process_Priority_Table_Entry *p_process_priority_table_entry) {
    if (is_process_priority_table_entry__empty(
                p_process_priority_table_entry)) {
        return true;
    }
    if (p_process_priority_table_entry->p_ptr_process__youngest_of__priority - 1
            < p_process_table->ptr_array_of__processes) {
        return false;
    }

    *--p_process_priority_table_entry->p_ptr_process__youngest_of__priority =
        *p_process_priority_table_entry->p_ptr_process__oldest_of__priority;
    *p_process_priority_table_entry->p_ptr_process__oldest_of__priority = 0;

    return true;
}

///
/// Similiar to the function, 
/// move_process_priorty_table_entry_up__one_in__ptr_array_of__processes
/// with the added behavior of inserting the given process as the new
/// youngest process in the priority.
///
/// NOTE: The non-empty process priority table entries of HIGHER priority
/// MUST be moved first.
///
bool add_process_to__process_priorty_table_entry_in__ptr_array_of__processes(
        Process_Table *p_process_table,
        Process_Priority_Table_Entry *p_process_priority_table_entry,
        Process *p_process) {
    if (!move_process_priorty_table_entry_up__one_in__ptr_array_of__processes(
                p_process_table, 
                p_process_priority_table_entry)) {
        return false;
    }
    *p_process_priority_table_entry->p_ptr_process__youngest_of__priority =
        p_process;
    return true;
}

bool 
remove_process_from__process_priority_table_entry_from__ptr_array_of__processes(
        Process_Priority_Table_Entry *p_process_priority_table_entry,
        Process *p_process) {
    if (p_process_priority_table_entry->p_ptr_process__oldest_of__priority
            < p_process_priority_table_entry->p_ptr_process__youngest_of__priority) {
        debug_error("remove_process_from__process_priority_table_entry_from__ptr_array_of__processes, process_priority_table has instrinsic violation.");
        return false;
    }
    if (p_process_priority_table_entry->p_ptr_process__oldest_of__priority
            == p_process_priority_table_entry->p_ptr_process__youngest_of__priority) {
        *p_process_priority_table_entry->p_ptr_process__oldest_of__priority = 0;
        p_process_priority_table_entry->p_ptr_process__oldest_of__priority = 0;
        p_process_priority_table_entry->p_ptr_process__youngest_of__priority = 0;
        return false;
    }

    Process **p_ptr_process =
        p_process_priority_table_entry->p_ptr_process__youngest_of__priority;
    do {
        if (*p_ptr_process == p_process) {
            *p_ptr_process = 
                *p_process_priority_table_entry->p_ptr_process__oldest_of__priority;
            *p_process_priority_table_entry->p_ptr_process__oldest_of__priority-- = 0;
            return true;
        }
    } while (++p_ptr_process <= p_process_priority_table_entry->p_ptr_process__oldest_of__priority);
    return false;
}

bool poll_next_p_process_from__process_priority_table_entry(
        Process_Priority_Table_Entry *p_process_priority_table_entry,
        Process **p_ptr_OUT_process) {
    if (is_process_priority_table_entry__empty(
                p_process_priority_table_entry)) {
        return 0;
    }
    Process *p_process =
        *p_process_priority_table_entry->p_ptr_process__current_priority_to__swap;
    bool is_table_done_polling =
        p_process
        == *p_process_priority_table_entry
        ->p_ptr_process__oldest_of__priority
        ;
    if (++p_process_priority_table_entry->p_ptr_process__current_priority_to__swap
            > p_process_priority_table_entry->p_ptr_process__oldest_of__priority) {
        p_process_priority_table_entry->p_ptr_process__current_priority_to__swap =
            p_process_priority_table_entry->p_ptr_process__youngest_of__priority;
    }
    *p_ptr_OUT_process = p_process;
    return is_table_done_polling;
}
