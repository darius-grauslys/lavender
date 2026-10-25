# Translation and Semantics

### Non-Injective Translation
Distinct sources collapse ot the same target.

### Translation Gap
One layer of the subsystem was never wired to a translator that another layer uses.

### Faithful
Preserves semantics not just syntax.

### Lossless
No information is destroyed/lost in the forward direction.
Some inverse exists in principle.

### Sound (translator)
Every output it produces is well-formed in the target language.

### Complete (translator)
Every valid source construct has a translation.
Parameterized by source grammar G every construct in G has a translation.

### Stub-real divergence
A placeholder satisfies structural checks but violates the semantic contract.

### Surface-form leakage
Syntactic surface of the input is copied ratherthan re-derived, polluting the output.
Output surface is inherited, not authored.

### Over Generalization
An invariant assumed to be universal is later found to be only locally true.

### Under Specified Dispatch
Multiple implementations share a head; no resolution rule is given.

### Aliasing Bug
Two names refer to the same entity and an assumption of one breaks the assumption of the other.

### Mode Confusion
The system is in a different mode than the caller assumes.

### State Desync
Two representations of the same thing have diverged.

### Qualified
Has explicit contextual assignment of a term's defition.
