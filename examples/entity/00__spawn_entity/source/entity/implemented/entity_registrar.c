#include "entity/implemented/entity_registrar.h"
#include "entity/implemented/entity__dummy.h"
#include "types/implemented/entity/entity_kind.h"

void register_entities(Entity_Manager *p_entity_manager) {
    // GEN-BEGIN
    // ***) Register every entity kind your game uses. The
    // entity manager looks up the function table by kind when an
    // entity is allocated (allocate_entity_*_in__entity_manager).
    register_entity_dummy_into__entity_manager(
            p_entity_manager);
    // GEN-END
}
