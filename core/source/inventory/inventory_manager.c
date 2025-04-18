#include "defines.h"
#include "defines_weak.h"
#include "inventory/inventory.h"
#include "numerics.h"
#include "platform_defines.h"
#include "random.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "serialization/identifiers.h"
#include "world/region.h"
#include <inventory/inventory_manager.h>

void initialize_inventory_manager(
        Inventory_Manager *p_inventory_manager) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)
            p_inventory_manager
                ->inventories, 
            MAX_QUANTITY_OF__INVENTORY, 
            sizeof(Inventory));
}

Inventory *allocate_p_inventory_using__this_uuid_in__inventory_manager(
        Inventory_Manager *p_inventory_manager,
        Identifier__u32 uuid) {
    return (Inventory*)get_next_available__allocation_in__contiguous_array(
            (Serialization_Header *)
            p_inventory_manager
                ->inventories, 
            MAX_QUANTITY_OF__INVENTORY, 
            uuid);
}

void release_inventory_in__inventory_manager(
        Inventory_Manager *p_inventory_manager,
        Inventory *p_inventory) {
#ifndef NDEBUG
    if (!p_inventory_manager) {
        debug_error("release_inventory_in__inventory_manager, p_inventory_manager == 0.");
        return;
    }
    if (!p_inventory) {
        debug_error("release_inventory_in__inventory_manager, p_inventory == 0.");
        return;
    }
    if (p_inventory - p_inventory_manager->inventories
            >= MAX_QUANTITY_OF__INVENTORY) {
        debug_error("release_inventory_in__inventory_manager, p_inventory was not allocated with this manager.");
        return;
    }
#endif

    initialize_inventory_as__empty(
            p_inventory);
}

Inventory *get_inventory_by__uuid_in__inventory_manager(
        Inventory_Manager *p_inventory_manager,
        Identifier__u32 identifier_for__inventory) {
    return (Inventory*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header *)p_inventory_manager
                ->inventories, 
            MAX_QUANTITY_OF__INVENTORY, 
            identifier_for__inventory);
}
