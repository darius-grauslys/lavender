# Invariants and Correctness

### Invariant
A predicate that holds across all observable states of a system.

### Representation Invariant
The relationship between abstract state and concrete storage.

### Loop Invariant
Holds at every iteration boundary.

### Abstraction Function
Maps concrete -> abstract.

### Conservation Law
A quantity preserved across transformations.

### Precondition
What must hold before a call.

### Postcondition
What the call guarantees on return.

### Canonical Form
A single representation for each equivalence class.
Is an output property, Normalizing is a systems property.

### Canonical Form Enforcement
Equivalence class has exactly one representative.

### Normalizing
Different reduction orders converge ot the same result (Church-Rosser).

### Confluent
Always reaches a canonical form; confluent + terminating.

### Fixpoint
f(x) == x an input unchanged by f.

### Boundary Condition
Behavior at the edge of a domain.

### Frame Condition
What a call is allowed to mutate and by negation what it must leave alone.

### Assertion
A runtime checked invariant.

### Static Analysis
Analyze without running.

### Conservative
Never over approximates; if it returns an answer the answer is correct.

### Contract-First
State preconditions, postconditions, and invariants. Only then does implementation proceed.
