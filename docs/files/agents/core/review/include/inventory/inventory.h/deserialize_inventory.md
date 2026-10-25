# deserialize_inventory

**File of origin:** `core/source/inventory/inventory.c`

## Semantic

Reads a serialized inventory from a file: first a 1-byte count of non-empty item stacks, then that many item stacks are deserialized into the inventory's `items` array. Sets `p_inventory->quantity_of__item_stacks` to the count read from the file.

## Pre-conditions

1. `p_PLATFORM_file_system_context` must be a valid, initialized platform file system context.
2. `p_item_manager` must be a valid, initialized item manager (used by `deserialize_item_stack` to resolve item kinds).
3. `p_serialization_request` must be non-null and `p_serialization_request->p_file_handler` must be a valid, open file handle positioned at the start of the serialized inventory data (i.e., at the quantity byte).
4. `p_inventory` must be non-null. The caller is responsible for ensuring the inventory is in a known state (e.g., initialized via `initialize_inventory` or `initialize_inventory_as__empty`) before deserialization, since this function does not clear pre-existing data.
5. The file at `p_file_handler` must contain at least one byte (the quantity count) followed by serialized item stack data matching the count.

## Post-conditions

1. If the initial read of the quantity byte succeeds, `quantity_of__serialized_item_stacks` is read from the file.
2. `p_inventory->quantity_of__item_stacks` is set to `quantity_of__serialized_item_stacks`.
3. For each index from 0 to `quantity_of__serialized_item_stacks - 1`, `deserialize_item_stack` is called to populate `p_inventory->items[index]`.
4. Returns `PLATFORM_Read_File_Error__None` if the initial quantity byte read succeeds (regardless of whether individual item stack deserialization succeeds, since those errors are not propagated).

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation does not fulfill its semantic intent. The function is intended to deserialize an inventory from file data, but:

- **No bounds validation on the deserialized count**: The `quantity_of__serialized_item_stacks` value is read directly from the file as a `Quantity__u8` (range 0–255) without any check against `INVENTORY_ITEM_MAXIMUM_QUANTITY_OF` (27). The serialize counterpart (`serialize_inventory`) naturally limits the count to at most 27 because it iterates over the fixed-size `items[27]` array. However, a corrupted or maliciously crafted file could contain a count exceeding 27, causing the loop to access `p_inventory->items[index]` out of bounds. This is a critical buffer over-read/overflow vulnerability.

- **Errors from `deserialize_item_stack` are silently swallowed**: `deserialize_item_stack` returns `void` and internally logs errors but does not propagate them. The function ignores whether each item stack deserialization succeeded, yet unconditionally sets `p_inventory->quantity_of__item_stacks` to the file-read count. This means the inventory's `quantity_of__item_stacks` may report more valid item stacks than were actually deserialized, leading to inconsistent state.

## Implementation Correctness

- **Type compatibility**: All types are compatible. `quantity_of__serialized_item_stacks` is `Quantity__u8` and `index_of__item_stack` is `Index__u8` — both `uint8_t`. The assignment to `p_inventory->quantity_of__item_stacks` (also `Quantity__u8`) is type-safe. No implicit conversions or truncation issues.

- **Undefined behavior — out-of-bounds array access**: If `quantity_of__serialized_item_stacks > INVENTORY_ITEM_MAXIMUM_QUANTITY_OF` (27), the loop in `deserialize_inventory` calls `get_p_item_stack_from__inventory_by__index(p_inventory, index_of__item_stack)` with an index ≥ 27, which performs `&p_inventory->items[index_of__item_stack]` — an out-of-bounds access on the `items` array. This is undefined behavior.

- **Validation gap**: The function performs no validation that `quantity_of__serialized_item_stacks` is within the bounds of the `items` array. This validation is the function's responsibility, not the caller's, because the function reads untrusted data from a file and uses it as an array index.

- **Missing null checks**: Unlike peer functions in the same file (e.g., `add_item_to__inventory`, `remove_p_item_stack_from__inventory`), this function lacks `#ifndef NDEBUG` null checks for `p_inventory` and `p_serialization_request`. While the caller may be expected to ensure validity, the absence of debug assertions makes debugging harder and is inconsistent with the codebase's conventions.

- **Misleading return value**: The function returns `error` at the end of the success path, but since the initial read error was already checked and returned early, `error` is always `PLATFORM_Read_File_Error__None` at that point. The return value does not reflect the success or failure of individual item stack deserialization.

## Side Effects

1. Reads from the file handle (`p_serialization_request->p_file_handler`), advancing the file position.
2. Mutates `p_inventory->items[0..quantity_of__serialized_item_stacks-1]` via `deserialize_item_stack`.
3. Mutates `p_inventory->quantity_of__item_stacks`, setting it to the count read from the file.
4. If `quantity_of__serialized_item_stacks` exceeds `INVENTORY_ITEM_MAXIMUM_QUANTITY_OF`, writes out-of-bounds to `p_inventory->items` (undefined behavior).
