#ifndef SESSION_TOKEN_H
#define SESSION_TOKEN_H

#include "defines.h"
#include "defines_weak.h"
#include "numerics.h"
#include "serialization/serialization_header.h"
static inline
Identifier__u32 get_uuid_u32_of__session_token_player_uuid_u64(
        Session_Token session_token) {
    // TODO: some bit info is lost in UUID branding here.
    // it might be worthwhile to improve the u64->u32 compression
    Identifier__u32 uuid_u32 = 
        (ARITHMETRIC_L_SHIFT(MASK(31), 31) & session_token.player_uuid) 
        ^ (MASK(31) & session_token.player_uuid);

    return BRAND_UUID(uuid_u32, GET_UUID_BRANDING(Lavender_Type__Player, 0));
}

#endif
