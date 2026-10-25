# Design Principles

### Interface Segregation
Many specific inferfaces are prefered over one generalized interface.
In otherwords, avoid multiple concerns directly access by a singular monolithic interface.
A notable exception is a composition of subinterfaces, and adhereance to law of demeter.

### Stable Dependency
Dependencies point in the direction of stability.
--help

### Single Source of Truth (SSOT)
Each fact lives in exactly one place.

### Don't Repeat Yourself (DRY)
No duplication of intent.

### Law of Demeter
Don't reach through objects.

### Dependency Injection
Recieve dependencies, don't fetch them.

### Inversion of Control (IoC)
The framework calls you, not vice versa.

### Composition over Inheritance
Build with parts, not the subtype hierarchies.

### Liskov Subsitution
Subtypes are subsitutable for their base.

### Open-closed
Open for extension closed for modification.

### Acyclic Dependencies
The dependency graph is acyclic.

### Encapsulation
Internals are hidden.

### Information Hiding
Clients depend on the interface, not the implementation.

### Refactoring
Behavior-preserving restructure.

### Coupled
Degree to which modules depend on each other.

### Cohesive
Each module's parts belong to each other.

### Orthogonal
Parts don't share concerns.

### Factorization
Decomposing a structure into orthogonal parts.

### Duality
Two views of the same thing.

### Spaghettification
Coupliung grows without bound; the dependency graph loses coherent structure.

### Sentinel
A distinguished value marking a special case.
