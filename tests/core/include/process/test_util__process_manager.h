#ifndef TEST_UTIL__PROCESS_MANAGER_H
#define TEST_UTIL__PROCESS_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void test_util__step_process_manager_until__this_many_proc_remains(
        Process_Manager *p_process_manager,
        Game *p_game,
        Quantity__u32 quantity_of__processes__u32);

#endif
