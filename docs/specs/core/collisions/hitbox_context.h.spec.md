# 1 Specification: core/include/collisions/hitbox_context.h

## 1.1 Overview

Provides the top-level abstraction layer for managing multiple hitbox manager
types. The `Hitbox_Context` owns a pool of `Hitbox_Manager_Instance` slots,
a per-type invocation table, and a per-type registration record table. It
allows the engine to support multiple hitbox representations (AABB, AAABBB,
etc.) through a unified interface using opaque pointers and callback tables.

The `Hitbox_Context` lives within the `Game` struct and is the primary
interface for hitbox system operations that are not specific to a single
hitbox manager type.

See `module_topology__collision.mmd` for the type hierarchy.

## 1.2 Dependencies

- `defines.h` (for `Hitbox_Context`, `Hitbox_Manager_Instance`,
  `Hitbox_Manager_Instance__Invocation_Table`,
  `Hitbox_Manager_Registration_Record`, `Hitbox_Manager_Type`,
  `Hitbox_Flags__u8`, `Identifier__u32`, `Quantity__u32`,
  `f_Hitbox_Manager__Allocator`, `f_Hitbox_Manager__Deallocator`,
  `f_Hitbox_Manager__Opaque_Property_Access_Of__Hitbox`,
  `MAX_QUANTITY_OF__HITBOX_MANAGERS`)
- `defines_weak.h` (forward declarations)

## 1.3 Types

### 1.3.1 Hitbox_Context (struct)

Defined in `defines.h`:

    typedef struct Hitbox_Context_t {
        Hitbox_Manager_Instance hitbox_manager_instances[
            MAX_QUANTITY_OF__HITBOX_MANAGERS];
        Hitbox_Manager_Instance__Invocation_Table hitbox_manager_instance__invocation_table[
            Hitbox_Manager_Type__Unknown];
        Hitbox_Manager_Registration_Record hitbox_manager_registration_records[
            Hitbox_Manager_Type__Unknown];
    } Hitbox_Context;

| Field | Type | Description |
|-------|------|-------------|
| `hitbox_manager_instances` | `Hitbox_Manager_Instance[MAX_QUANTITY_OF__HITBOX_MANAGERS]` | Pool of manager instance slots. Each slot can hold one allocated hitbox manager of any registered type. |
| `hitbox_manager_instance__invocation_table` | `Hitbox_Manager_Instance__Invocation_Table[Hitbox_Manager_Type__Unknown]` | Per-type callback table. Indexed by `Hitbox_Manager_Type`. Contains allocator, deallocator, and opaque property access callbacks. |
| `hitbox_manager_registration_records` | `Hitbox_Manager_Registration_Record[Hitbox_Manager_Type__Unknown]` | Per-type metadata. Describes component sizes, quantities, and fractional precision for each registered hitbox type. |

### 1.3.2 Hitbox_Manager_Instance (struct)

Defined in `defines.h`:

    typedef struct Hitbox_Manager_Instance_t {
        Serialization_Header _serialization_header;
        void *pVM_hitbox_manager;
        Hitbox_Manager_Type type_of__hitbox_manager;
    } Hitbox_Manager_Instance;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for the manager instance. Used for lookup. |
| `pVM_hitbox_manager` | `void*` | Opaque pointer to the concrete hitbox manager (e.g. `Hitbox_AABB_Manager*`). |
| `type_of__hitbox_manager` | `Hitbox_Manager_Type` | Discriminator for the concrete type. |

### 1.3.3 Hitbox_Manager_Instance__Invocation_Table (struct)

Defined in `defines.h`:

    typedef struct Hitbox_Manager_Instance__Invocation_Table_t {
        f_Hitbox_Manager__Allocator f_hitbox_manager__allocator;
        f_Hitbox_Manager__Deallocator f_hitbox_manager__deallocator;
        f_Hitbox_Manager__Opaque_Property_Access_Of__Hitbox
            f_hitbox_manager__get_properties_of__hitbox;
    } Hitbox_Manager_Instance__Invocation_Table;

### 1.3.4 Hitbox_Manager_Registration_Record (struct)

Defined in `defines.h`:

    typedef struct Hitbox_Manager_Registration_Record_t {
        u8 size_of__components__dimensions;
        u8 size_of__components__pos_vel;
        u8 size_of__components__acceleration;
        u8 quantity_of__components__dimensions;
        u8 quantity_of__components__pos_vel_acc;
        u8 fractional_percision_of__dimensions;
        u8 fractional_percision_of__pos_vel;
        u8 fractional_percision_of__acceleration;
    } Hitbox_Manager_Registration_Record;

| Field | Description |
|-------|-------------|
| `size_of__components__dimensions` | Byte size of each dimension component (e.g. 4 for `u32`). |
| `size_of__components__pos_vel` | Byte size of each position/velocity component (e.g. 4 for `i32F4`). |
| `size_of__components__acceleration` | Byte size of each acceleration component (e.g. 2 for `i16F8`). |
| `quantity_of__components__dimensions` | Number of dimension components (e.g. 2 for width+height). |
| `quantity_of__components__pos_vel_acc` | Number of position/velocity/acceleration components (e.g. 3 for x,y,z). |
| `fractional_percision_of__dimensions` | Fractional bit count for dimensions (e.g. 0). |
| `fractional_percision_of__pos_vel` | Fractional bit count for position/velocity (e.g. 4). |
| `fractional_percision_of__acceleration` | Fractional bit count for acceleration (e.g. 8). |

### 1.3.5 Hitbox_Manager_Type (enum)

Defined in `defines.h`:

    typedef enum Hitbox_Manager_Type_t {
        Hitbox_Manager_Type__Default,
        Hitbox_Manager_Type__AABB = Hitbox_Manager_Type__Default,
        Hitbox_Manager_Type__AAABBB,
        Hitbox_Manager_Type__Unknown
    } Hitbox_Manager_Type;

### 1.3.6 Constants

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__HITBOX_MANAGERS` | 8 | Maximum number of simultaneously allocated hitbox manager instances. |
| `MAX_QUANTITY_OF__HITBOX` | 256 | Collective hitbox limit across all allocated pools. |
| `OPAQUE_HITBOX_ACCESS__SET` | `true` | Pass to `opaque_access_to__hitbox` to write properties. |
| `OPAQUE_HITBOX_ACCESS__GET` | `false` | Pass to `opaque_access_to__hitbox` to read properties. |

### 1.3.7 Clarity Macros

These macros exist solely to improve readability at registration call sites:

| Macro | Expands To | Description |
|-------|------------|-------------|
| `QUANTITY_OF__HITBOX_COMPONENTS(description, n)` | `(n)` | Documents the meaning of a component count argument. |
| `SIZE_OF__HITBOX_COMPONENTS(description, n)` | `(n)` | Documents the meaning of a component size argument. |
| `FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS(description, n)` | `(n)` | Documents the meaning of a fractional precision argument. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_hitbox_context` | `(Hitbox_Context*) -> void` | Initializes all manager instance slots as deallocated, clears invocation tables and registration records. |

### 1.4.2 Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_hitbox_manager` | `(Hitbox_Context*, f_Hitbox_Manager__Allocator, f_Hitbox_Manager__Deallocator, f_Hitbox_Manager__Opaque_Property_Access_Of__Hitbox, Hitbox_Manager_Type, u8 qty_dims, u8 qty_pos_vel_acc, u8 size_dims, u8 size_pos_vel, u8 size_acc, u8 frac_dims, u8 frac_pos_vel, u8 frac_acc) -> void` | Registers a hitbox manager type by populating its invocation table entry and registration record. Must be called before allocating managers of that type. |

### 1.4.3 Manager Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_hitbox_manager_from__hitbox_context` | `(Hitbox_Context*, Identifier__u32 uuid, Hitbox_Manager_Type, Quantity__u32 quantity) -> Hitbox_Manager_Instance*` | `Hitbox_Manager_Instance*` | Allocates a manager instance slot, invokes the registered allocator callback to create the concrete manager, and stores the result. Returns the instance, or NULL on failure. |
| `release_hitbox_manager_from__hitbox_context` | `(Hitbox_Context*, Identifier__u32 uuid) -> void` | `void` | Finds the manager instance by UUID, invokes the registered deallocator callback, and marks the slot as deallocated. |

### 1.4.4 Hitbox Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_pV_hitbox_from__hitbox_context` | `(Hitbox_Context*, Identifier__u32 uuid_of_manager, Identifier__u32 uuid_of_hitbox) -> void*` | `void*` | Allocates a hitbox from the specified manager instance. Returns an opaque pointer to the hitbox. |

### 1.4.5 Opaque Property Access

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `opaque_access_to__hitbox` | `(Hitbox_Context*, Identifier__u32 uuid_of_manager, Identifier__u32 uuid_of_hitbox, void* pV_dims, void* pV_pos, void* pV_vel, void* pV_acc, Hitbox_Flags__u8*, bool is_set) -> bool` | `bool` | Resolves the hitbox by UUID, then invokes the registered opaque property access callback. Any non-null optional pointer is read from or written to depending on `is_set`. Returns true if the access was performed. |

### 1.4.6 Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context` | `(Hitbox_Context*, Identifier__u32 uuid) -> Hitbox_Manager_Instance*` | `Hitbox_Manager_Instance*` | Finds a manager instance by UUID. Returns an invalid instance (check with `is_p_hitbox_manager_instance__valid`) if not found. Reports no error upon failure to find. |
| `get_max_quantity_of__hitboxes_in__hitbox_manager` | `(Hitbox_Context*, Identifier__u32 uuid) -> Quantity__u32` | `Quantity__u32` | Returns the pool capacity of the specified manager instance. |
| `get_pV_hitbox_from__hitbox_context` | `(Hitbox_Context*, Identifier__u32 uuid_of_manager, Identifier__u32 uuid_of_hitbox) -> void*` | `void*` | Returns an opaque pointer to the hitbox with the given UUID in the specified manager. |

### 1.4.7 Convenience Accessor (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_pV_hitbox_manager_from__hitbox_context` | `(Hitbox_Context*, Identifier__u32 uuid) -> void*` | `void*` | Returns the opaque `pVM_hitbox_manager` pointer from the manager instance with the given UUID. Delegates to `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context`. |

## 1.5 Agentic Workflow

### 1.5.1 Hitbox Context Lifecycle

    [Uninitialized]
        |
        initialize_hitbox_context(p_hitbox_context)
        |
    [Initialized, No Registrations]
        |
        register_hitbox_manager(p_hitbox_context, ..., Hitbox_Manager_Type__AABB, ...)
        |
    [Has Registered Types]
        |
        allocate_hitbox_manager_from__hitbox_context(
            p_hitbox_context, uuid, Hitbox_Manager_Type__AABB, 256)
        |
    [Has Allocated Manager Instances]
        |
        allocate_pV_hitbox_from__hitbox_context(
            p_hitbox_context, manager_uuid, hitbox_uuid)
        |
    [Manager Has Allocated Hitboxes]
        |
        opaque_access_to__hitbox(
            p_hitbox_context, manager_uuid, hitbox_uuid,
            NULL, &position, NULL, NULL, NULL,
            OPAQUE_HITBOX_ACCESS__GET)
        |
        release_hitbox_manager_from__hitbox_context(
            p_hitbox_context, manager_uuid)
        |
    [Manager Slot Freed]

### 1.5.2 Registration Pattern

Registration is typically performed once during game initialization by the
platform-specific `hitbox_manager_registrar.h`:

    void register_hitbox_managers(Hitbox_Context *p_hitbox_context) {
        register_hitbox_manager(
            p_hitbox_context,
            f_hitbox_manager__allocator_AABB,
            f_hitbox_manager__deallocator_AABB,
            f_hitbox_manager__opaque_property_access_of__hitbox_AABB,
            Hitbox_Manager_Type__AABB,
            QUANTITY_OF__HITBOX_COMPONENTS("width, height", 2),
            QUANTITY_OF__HITBOX_COMPONENTS("x, y, z", 3),
            SIZE_OF__HITBOX_COMPONENTS("u32", sizeof(u32)),
            SIZE_OF__HITBOX_COMPONENTS("i32F4", sizeof(i32F4)),
            SIZE_OF__HITBOX_COMPONENTS("i16F8", sizeof(i16F8)),
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS("none",
                FRACTIONAL_PERCISION_0__BIT_SIZE),
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS("4bit",
                FRACTIONAL_PERCISION_4__BIT_SIZE),
            FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS("8bit",
                FRACTIONAL_PERCISION_8__BIT_SIZE));
    }

### 1.5.3 Opaque Access Pattern

The opaque access system is designed for infrequent, type-agnostic hitbox
manipulation. For performance-critical code, obtain the concrete manager
pointer and work with it directly:

    // Slow (opaque, type-agnostic):
    opaque_access_to__hitbox(ctx, mgr_uuid, hb_uuid,
        NULL, &pos, NULL, NULL, NULL, OPAQUE_HITBOX_ACCESS__GET);

    // Fast (concrete, type-specific):
    Hitbox_AABB_Manager *p_mgr = get_pV_hitbox_manager_from__hitbox_context(
        ctx, mgr_uuid);
    Hitbox_AABB *p_hb = get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
        p_mgr, hb_uuid);
    Vector__3i32F4 pos = p_hb->position__3i32F4;

### 1.5.4 Preconditions

- `initialize_hitbox_context`: `p_hitbox_context` must be non-null.
- `register_hitbox_manager`: The type must not already be registered.
  All callback pointers must be non-null.
- `allocate_hitbox_manager_from__hitbox_context`: The type must be
  registered. There must be an available instance slot.
- `opaque_access_to__hitbox`: The manager and hitbox UUIDs must be valid.

### 1.5.5 Postconditions

- After `register_hitbox_manager`: The invocation table and registration
  record for the given type are populated.
- After `allocate_hitbox_manager_from__hitbox_context` (success): The
  returned instance has a valid UUID, a non-null `pVM_hitbox_manager`,
  and `is_p_hitbox_manager_instance__valid` returns true.
- After `release_hitbox_manager_from__hitbox_context`: The instance slot
  is available for reuse. `is_p_hitbox_manager_instance__valid` returns
  false for the old UUID.

### 1.5.6 Error Handling

- `allocate_hitbox_manager_from__hitbox_context` returns NULL if no
  instance slots are available or if the allocator callback fails.
- `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context` returns
  an invalid instance (not an error) if the UUID is not found.
- `opaque_access_to__hitbox` returns false if the hitbox or manager cannot
  be resolved.
- Debug builds may call `debug_error` or `debug_abort` on invalid arguments.
