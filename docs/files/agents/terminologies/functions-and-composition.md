# Functions and Composition

### Composable
The output of f is a valid input type of g.

### Associative
f(f(a,b),c) = f(a, f(b,c)), can be regrouped.

### Commutative
f(a,b) == f(b,a) - operand swappable.

### Injective
Distinct sources map to distinct targets.

### Surjective
Every target has a source.

### Bijective
Both Injective and Surjective, lossless in both directions.

### Homomorphic
Structure preserving in one direction.
f(a \open_dot b) = f(a) \dot f(b)
where \open_dot is source structure, and \dot is target structure.

### Isomorphic
Bijective and structure preserving a<b> -> f(a) < f(b) in both directions.

### Catamorphism
Fold - collapse a structure to a value.

### Anamorphism
Build to a structure from a seed.

### Hylomorphism
Unfold then fold (Catamorphism + Anamorphism).

### Combinator
A function that builds things out of a kind from things of the same kind.

### Lensing Structure
A structure with a focused subpart and a way to put it back.
.get() -> X, .set(X)

### Pure
Same input -> same ouput, no side effects.

### Idempotence
f(f(x)) == f(x)
Reapply yields no futher mutations.

### Memoized
Cache results of pure calls.

### Referentially Transparent
A call can be replaced with a cached result without changing the program's meaning.

### Deterministic
Same input -> same output, side effects are allowed, but traceable+reproducable.
