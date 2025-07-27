#ifndef PROCESS_PRIORITY_TABLE_ENTRY_H
#define PROCESS_PRIORITY_TABLE_ENTRY_H

#include "defines.h"
#include "defines_weak.h"

void initialize_process_priority_table_entry(
        Process_Priority_Table_Entry *p_process_priority_table_entry,
        Process **p_ptr_process__first);

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
        Process_Priority_Table_Entry *p_process_priority_table_entry);

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
        Process_Priority_Table_Entry *p_process_priority_table_entry);

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
        Process *p_process);

bool 
remove_process_from__process_priority_table_entry_from__ptr_array_of__processes(
        Process_Priority_Table_Entry *p_process_priority_table_entry,
        Process *p_process);

///
/// Returns true if the table is wrapping around.
/// In otherwords, returns true if the last process in the table entry
/// was polled, and its time to move to the next table entry.
///
bool poll_next_p_process_from__process_priority_table_entry(
        Process_Priority_Table_Entry *p_process_priority_table_entry,
        Process **p_ptr_OUT_process);

static inline
bool is_process_priority_table_entry__empty(
        Process_Priority_Table_Entry *p_process_priority_table_entry) {
    return p_process_priority_table_entry->p_ptr_process__oldest_of__priority
        == 0
        || p_process_priority_table_entry->p_ptr_process__youngest_of__priority
        == 0
        ;
}

static inline
Quantity__u32 get_quantity_of__processes_in__process_priority_table_entry(
        Process_Priority_Table_Entry *p_process_priority_table_entry) {
    return p_process_priority_table_entry->p_ptr_process__oldest_of__priority
        - p_process_priority_table_entry->p_ptr_process__youngest_of__priority;
}

#endif
