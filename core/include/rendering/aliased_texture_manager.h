#ifndef ALIASED_TEXTURE_MANAGER_H
#define ALIASED_TEXTURE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void initialize_aliased_texture_manager(
        Aliased_Texture_Manager *p_aliased_texture_manager);

///
/// WARNING: You do not own the returned texture.
/// NOTE: repeated names will shadow textures in an
/// unpredictable manner.
/// 
/// returns true if failure occurs.
///
bool allocate_texture_with__alias(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str,
        Texture_Flags texture_flags,
        Texture *p_OUT_texture);

bool load_texture_from__path_with__alias(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str,
        Texture_Flags texture_flags,
        const char *c_str__path,
        Texture *p_OUT_texture);

Identifier__u32 get_uuid_of__aliased_texture(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str);

bool get_texture_by__alias(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str,
        Texture *p_OUT_texture);

bool get_texture_by__uuid(
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Identifier__u32 uuid__u32,
        Texture *p_OUT_texture);

void release_all_aliased_textures(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Aliased_Texture_Manager *p_aliased_texture_manager);

void release_aliased_texture_by__alias(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Texture_Name__c_str name_of__texture__c_str);

void release_aliased_texture_by__uuid(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Aliased_Texture_Manager *p_aliased_texture_manager,
        Identifier__u32 uuid__u32);

#endif
