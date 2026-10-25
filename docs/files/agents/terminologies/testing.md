# Testing

### Round Trip Property
Encode + Decode as a property.

### Round Trip Safe
A specific pair (encode,decode) satisfies encode(decode(x)) == x
and decode(encode(y)) == y.

### Round Trip Check
encode(decode(x)) == x as a test propety.

### Differential Testing
Compare two implementations on the same inputs.

### Fuzzing
Feed malformed/random inputs to find crashes.

### Equivalence Check
Prove tow programs compute the same function.

### Golden-file Test
Compare against a fixed expected output.

### Property Based Testing
Generate random inputs, check an invariant holds.

### Mutation Testing
Mutate the code, see if the tests catch it.

### Symbolic Execution
Explore paths with symbolic inputs instead of conrete inputs (lazy parameter descent).

### Concolic Testing
Combine concrete + symbolic execution.

### Model Checking
Exhaustively enumerate the state space.

### Acceptance Predicate
The strongest check the system actually runs.
P0 && (P1 || P2 ... || PN) - P0 is the strongest check.

### Lint Gate
Syntactic well-formedness check.
