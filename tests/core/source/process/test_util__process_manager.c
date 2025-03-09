#include "process/test_util__process_manager.h"
#include "defines_weak.h"
#include "process/process_manager.h"

void test_util__step_process_manager_until__this_many_proc_remains(
        Process_Manager *p_process_manager,
        Game *p_game,
        Quantity__u32 quantity_of__processes__u32) {
    Quantity__u32 quantity_of__processes_remaining__u32 =
        get_quantity_of__processes_in__process_manager(
                p_process_manager);
    while (
            quantity_of__processes_remaining__u32
            <= quantity_of__processes__u32) {
        poll_process_manager(
                p_process_manager,
                p_game);
        quantity_of__processes_remaining__u32 =
            get_quantity_of__processes_in__process_manager(
                    p_process_manager);
    }
}
