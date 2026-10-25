# State and Concurrency

### Stateful
Whether memory persists across calls. Opposite of Stateless.

### Persistent
Operations preserve old versions.

### Immutable
Never changes after construction.

### Snapshot (state)
A captured immutable state.

### Delta (state)
A representation of the changes between two snapshots.

### Patch (state)
A transformation to apply to a snapshot.

### Replay (state)
Reapplying a sequence of deltas from a snapshot.

### Snapshot + Log
Periodic full state + delta log between.

### CRDT
Conflict free replciated data type.
Any merge order converges.

### CQRS (state)
Separate the read model from the write model.

### Delta Sourcing (state)
Store the log of deltas; derive the state of replay.

### Event Sourcing
Store the log, derive the state.
Auditable, replayable.

### Pessimistic Concurrency
Acquire locks before writing.

### Optimistic Concurrency
Assume no conflict, detect on commit.

### Crash-only
Restart instead of clean shutdown.

### Lost Update
Concurrent writes; the loser's change is silently overwritten.

### Thundering Herd
Many writers wake on one event and contend.

### Time of check time of use (TOCTOU)
Condition holds at check time but not at use time.

### Reentrant
Can be interrupted mid-execution and re-entered safely.

### Terminating
Always halts.

### Atomic
No intermediate observable state.

### Cascade Failure
A failure in one component triggers failures in dependents.
