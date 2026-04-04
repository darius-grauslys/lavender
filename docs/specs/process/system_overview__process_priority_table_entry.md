# System Overview: Process Priority Table Entry

## Purpose

The `Process_Priority_Table_Entry` manages a single priority level's
contiguous region within the `Process_Table`'s pointer array. It provides
the low-level operations for insertion, removal, compaction, and
round-robin polling within that region.

These functions are internal to the process scheduling system. They are
called by `Process_Table` operations and should not be called directly
by game code.

## Architecture

### Data Layout

    Process_Priority_Table_Entry
    +-- Process **p_ptr_process__youngest_of__priority
    |   (points to the start of this priority's region in the pointer array)
    |
    +-- Process **p_ptr_process__oldest_of__priority
    |   (points to the end of this priority's region in the pointer array)
    |
    +-- Process **p_ptr_process__current_priority_to__swap
        (round-robin cursor: advances through the region each poll cycle)

### Relationship to Pointer Array

Each `Process_Priority_Table_Entry` delimits a contiguous slice of the
`Process_Table`'s `ptr_array_of__processes`:

    ptr_array_of__processes:
    [...| youngest  P_a  P_b  P_c  oldest |...]
         ^                          ^
         |                          |
         p_ptr_process__youngest    p_ptr_process__oldest

The region contains `(oldest - youngest)` process pointers. When the
region is empty, both delimiter pointers are null (or equal, depending
on initialization).

### Key Types

| Type | Role |
|------|------|
| `Process_Priority_Table_Entry` | Manages one priority level's region. Three pointers into the shared pointer array. |
| `Process_Table` | Parent structure. Owns the pointer array and all priority entries. |
| `Process` | The cooperative task unit referenced by pointers in the region. |

## Region Management

### Empty State

A priority level is empty when:

    is_process_priority_table_entry__empty(p_entry)
        -> Returns true if either delimiter pointer is NULL.

An empty entry has zero processes:

    get_quantity_of__processes_in__process_priority_table_entry(p_entry)
        -> Returns 0 when empty.

### Region Size

    Quantity__u32 count =
        get_quantity_of__processes_in__process_priority_table_entry(p_entry);
        -> Returns (p_ptr_process__oldest - p_ptr_process__youngest).

## Compaction Operations

Because the pointer array is shared across all priority levels, inserting
or removing a process at one priority level requires shifting adjacent
priority levels to maintain contiguous regions.

### Moving a Region Up (Towards Higher Indices)

    move_process_priorty_table_entry_up__one_in__ptr_array_of__processes(
        p_process_table, p_entry);

Shifts every pointer in this entry's region up by one slot in the array.
The slot at `youngest` becomes free. Both delimiter pointers and the
round-robin cursor are incremented.

**When used:** Before inserting into a lower-priority level. Higher-priority
regions must be moved up first to make room.

**Ordering constraint:** When inserting into priority N, move priority 0
up first, then priority 1, ..., then priority N-1.

### Moving a Region Down (Towards Lower Indices)

    move_process_priorty_table_entry_down__one_in__ptr_array_of__processes(
        p_process_table, p_entry);

Shifts every pointer in this entry's region down by one slot. The slot at
`oldest` becomes free. Both delimiter pointers and the round-robin cursor
are decremented.

**When used:** After removing from a lower-priority level. Higher-priority
regions must be moved down afterwards to fill the gap.

**Ordering constraint:** When removing from priority N, move priority N-1
down first, then N-2, ..., then priority 0.

### Visual Example

Starting state (priority 0 and priority 1):

    ptr_array: [A B | C D E]
    P0: youngest=&[0], oldest=&[1]  -> [A, B]
    P1: youngest=&[2], oldest=&[4]  -> [C, D, E]

**Insert into P1 (move P0 up first):**

    move_process_priorty_table_entry_up__one(table, &P0):
        ptr_array: [_ A B | C D E]  (shifted A,B right by one)
        P0: youngest=&[1], oldest=&[2]

    add_process_to__process_priorty_table_entry(table, &P1, G):
        ptr_array: [_ A B G | C D E]
        P1: youngest=&[3], oldest=&[6]  -> [G, C, D, E]

**Remove D from P1 (then move P0 down):**

    remove_process_from__process_priority_table_entry(&P1, D):
        ptr_array: [_ A B G | C E _]  (D removed, region compacted)
        P1: youngest=&[3], oldest=&[5]  -> [G, C, E]

    move_process_priorty_table_entry_down__one(table, &P0):
        ptr_array: [A B G | C E _]  (shifted A,B left by one)
        P0: youngest=&[0], oldest=&[1]

## Insertion

    add_process_to__process_priorty_table_entry_in__ptr_array_of__processes(
        p_process_table, p_entry, p_process);

1. Moves the entry's region up by one slot (calls
   `move_process_priorty_table_entry_up__one`).
2. Writes `p_process` into the newly freed youngest slot.
3. The process becomes the youngest in this priority level.

**Precondition:** All higher-priority entries MUST have already been moved
up before calling this function.

**Returns:** false if the operation fails (e.g. the pointer array is full).

## Removal

    remove_process_from__process_priority_table_entry_from__ptr_array_of__processes(
        p_entry, p_process);

1. Searches the region for the pointer matching `p_process`.
2. Removes it by shifting subsequent pointers within the region to fill
   the gap.
3. Decrements the oldest delimiter.

**Postcondition:** The caller MUST then move all higher-priority entries
down by one to fill the gap left at the boundary.

**Returns:** false if the process is not found in this entry's region.

## Round-Robin Polling

    poll_next_p_process_from__process_priority_table_entry(
        p_entry, &p_ptr_OUT_process);

Advances the round-robin cursor (`p_ptr_process__current_priority_to__swap`)
by one position within the region and writes the process at that position
to `p_ptr_OUT_process`.

**Return value:**
- `false`: A process was returned and the cursor has not yet wrapped around.
  The caller should continue polling this priority level.
- `true`: The cursor has wrapped around. All processes in this priority
  level have been polled for this cycle. The caller should advance to the
  next priority level.

If the entry is empty, returns `true` immediately (skip to next level).

### Round-Robin Fairness

The cursor persists across poll cycles. Each cycle, polling starts from
where the previous cycle left off, ensuring that no process is
systematically starved within its priority level.

    Cycle 1: poll A, poll B, poll C (wrap) -> advance to next priority
    Cycle 2: poll B, poll C, poll A (wrap) -> advance to next priority
    Cycle 3: poll C, poll A, poll B (wrap) -> advance to next priority

## Lifecycle

### 1. Initialization

    initialize_process_priority_table_entry(p_entry, p_ptr_process__first);
        -> p_ptr_process__youngest_of__priority = p_ptr_process__first
        -> p_ptr_process__oldest_of__priority = p_ptr_process__first
           (or NULL for empty)
        -> p_ptr_process__current_priority_to__swap = p_ptr_process__first

### 2. Steady State

During normal operation, the entry's region grows and shrinks as processes
are added and removed. The round-robin cursor advances each poll cycle.

### 3. Empty State

When the last process is removed, the entry becomes empty. Polling an
empty entry immediately returns `true` (wrap), causing the scheduler to
skip to the next priority level.

## Capacity Constraints

- The maximum number of processes across all priority levels is
  `PROCESS_MAX_QUANTITY_OF` (512). There is no per-priority-level limit
  beyond the total array capacity.
- The entry does not own any memory — it holds three pointers into the
  `Process_Table`'s pointer array.

## Relationship to Process_Table

The `Process_Priority_Table_Entry` is a sub-component of `Process_Table`:

| Concern | Managed By |
|---------|------------|
| Pointer array ownership | `Process_Table` |
| Per-priority region delimiting | `Process_Priority_Table_Entry` |
| Cross-priority compaction ordering | `Process_Table` (calls entry functions in correct order) |
| Round-robin cursor advancement | `Process_Priority_Table_Entry` |
| Priority level advancement during polling | `Process_Table` |

The `Process_Table` is responsible for calling the entry functions in the
correct order during insertion and removal. The entry functions themselves
do not enforce cross-priority ordering — they only manage their own region.
