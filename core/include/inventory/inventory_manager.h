#ifndef INVENTORY_MANAGER_H
#define INVENTORY_MANAGER_H

#include "defines_weak.h"
#include "game.h"
#include <defines.h>

void initialize_inventory_manager(
        Inventory_Manager *p_inventory_manager);

Inventory *allocate_p_inventory_using__this_uuid_in__inventory_manager(
        Inventory_Manager *p_inventory_manager, 
        Identifier__u32 uuid);

void release_inventory_in__inventory_manager(
        Inventory_Manager *p_inventory_manager,
        Inventory *p_inventory);

Inventory *get_inventory_by__uuid_in__inventory_manager(
        Inventory_Manager *p_inventory_manager,
        Identifier__u32 identifier_for__inventory);

#endif
