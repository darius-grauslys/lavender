#include "defines.h"
#include "defines_weak.h"
#include "degree.h"
#include "game.h"
#include "process/process.h"
#include "raycast/ray.h"
#include "sort/sort_list/heap_sort.h"
#include "sort/sort_list/sort_list.h"
#include "vectors.h"
#include "world/chunk_manager.h"
#include "world/path_finding/path.h"
#include "world/path_finding/path_list.h"
#include "world/tile.h"
#include "world/world.h"
#include <world/path_finding/process/process_path_finding.h>

void m_process__path_find(
        Process *p_this_process,
        Game *p_game) {
    LOOP_PROCESS(p_this_process) {
    }
}

void initialize_process_for__path_finding(
        Process *p_process,
        Path_List *p_path_list,
        Quantity__u32 quantity_of__steps_per_cycle) {
    initialize_process(
            p_process, 
            m_process__path_find, 
            0,
            p_path_list,
            quantity_of__steps_per_cycle);

    initialize_sort_list_as__heap(
            p_path_list->p_min_heap_for__paths);
    set_sort_list__sort_heuristic(
            p_path_list->p_min_heap_for__paths, 
            f_sort_heuristic__min_path);

    initialize_sort_list_as__heap(
            p_path_list->p_max_heap_for__paths);
    set_sort_list__sort_heuristic(
            p_path_list->p_max_heap_for__paths, 
            f_sort_heuristic__max_path);
}
