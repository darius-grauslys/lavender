#ifndef PROCESS_TABLE_H
#define PROCESS_TABLE_H

#include "defines.h"

void initialize_process_table(
        Process_Table *p_process_table);

bool add_process_to__process_table(
        Process_Table *p_process_table,
        Process *p_process);

void remove_process_from__process_table(
        Process_Table *p_process_table,
        Process *p_process);

void begin_polling_of__process_table(
        Process_Table *p_process_table);

Process *poll_next_p_process_from__process_table(
        Process_Table *p_process_table);

Quantity__u32 get_quantity_of__processes_in__process_table(
        Process_Table *p_process_table);

#endif
