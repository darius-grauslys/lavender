# Terminology Index

This directory contains a collection of terminology definitions organized by theme.
The original monolithic `terminology.md` has been split into the sub-files below.

## Categories

| File | Topic | Terms |
|------|-------|-------|
| [functions-and-composition.md](functions-and-composition.md) | Structure-preserving mappings, folds, unfolds, and functional properties | Associative, Bijective, Catamorphism, Commutative, Combinator, Composable, Deterministic, Homomorphism, Idempotence, Injective, Isomorphic, Lensing Structure, Memoized, Pure, Referentially Transparent, Round Trip Safe, Surjective, Anamorphism, Hylomorphism |
| [type-systems.md](type-systems.md) | Types, type constructors, and type-level invariants | Abstract Data Type (ADT), Algebraic Data Type, Functorial, Monadic, Product Type, Strict, Tagged Union, Total, Type Invariant |
| [data-structures.md](data-structures.md) | Concrete and abstract data structures | Affine, B-tree, Cons-list, Finger Tree, Hash Trie, Linear, Trie, Zipper |
| [invariants-and-correctness.md](invariants-and-correctness.md) | Invariants, contracts, refinement, and static analysis | Abstraction Function, Assertion, Boundary Condition, Canonical Form, Canonical Form Enforcement, Confluent, Conservation Law, Contract-First, Fixpoint, Frame Condition, Invariant, Loop Invariant, Normalizing, Postcondition, Precondition, Representation Invariant, Static Analysis, Conservative |
| [design-principles.md](design-principles.md) | SOLID-like principles, coupling, cohesion, and modularity | Acyclic Dependencies, Composition over Inheritance, Cohesive, Coupled, Duality, Encapsulation, Factorization, Information Hiding, Interface Segregation, Inversion of Control (IoC), Law of Demeter, Liskov Subsitution, Orthogonal, Refactoring, Sentinel, Single Source of Truth (SSOT), Spaghettification, Stable Dependency, Don't Repeat Yourself (DRY), Dependency Injection, Open-closed |
| [architecture.md](architecture.md) | Layering and architectural constraints | Layer Architecture, Layered Architecture, Statified |
| [testing.md](testing.md) | Testing strategies and verification techniques | Acceptance Predicate, Concolic Testing, Differential Testing, Equivalence Check, Fuzzing, Golden-file Test, Lint Gate, Model Checking, Mutation Testing, Property Based Testing, Round Trip Check, Round Trip Property, Symbolic Execution, Round Trip Safe |
| [state-and-concurrency.md](state-and-concurrency.md) | State management, persistence, and concurrency control | Atomic, Cascade Failure, Crash-only, CRDT, CQRS (state), Delta (state), Delta Sourcing (state), Event Sourcing, Immutable, Lost Update, Optimistic Concurrency, Patch (state), Persistent, Pessimistic Concurrency, Reentrant, Replay (state), Snapshot (state), Snapshot + Log, Stateful, Terminating, Thundering Herd, Time of check time of use (TOCTOU) |
| [translation-and-semantics.md](translation-and-semantics.md) | Compiler/translator correctness and semantic preservation | Aliasing Bug, Complete (translator), Faithful, Lossless, Mode Confusion, Non-Injective Translation, Over Generalization, Qualified, Sound (translator), State Desync, Stub-real divergence, Surface-form leakage, Translation Gap, Under Specified Dispatch |
| [algorithms.md](algorithms.md) | Algorithm design patterns and techniques | Backtracking, Bisection, Batched, Branch and Bound, Divide and Conquer, Dynamic Programming, Fork-join, Greedy, Map-reduce, Monotonic, Pipelined, Short-Circuit, Sliding Window, Streaming, Topological Sort, Tracing, Two Pointer |
| [methodology.md](methodology.md) | Development methodologies and workflow patterns | Bi-directional Development, Interface Development, Invariant Driven Development, Literate Programming, Protocol First Design, Provenance Tracking, Refinement Calculus, Reflection, Scaffolding, Specification-First, Test Driven Development, Type-driven Development |

## Alphabetical Listing

**Abstract Data Type (ADT)** — type-systems  
**Abstraction Function** — invariants-and-correctness  
**Acceptance Predicate** — testing  
**Acyclic Dependencies** — design-principles  
**Affine (Data structure)** — data-structures  
**Algebraic Data Type** — type-systems  
**Aliasing Bug** — translation-and-semantics  
**Anamorphism** — functions-and-composition  
**Assertion** — invariants-and-correctness  
**Associative** — functions-and-composition  
**Atomic** — state-and-concurrency  
**B-tree** — data-structures  
**Backtracking** — algorithms  
**Batched** — algorithms  
**Bi-directional Development** — methodology  
**Bijective** — functions-and-composition  
**Bisection** — algorithms  
**Boundary Condition** — invariants-and-correctness  
**Branch and Bound** — algorithms  
**CRDT** — state-and-concurrency  
**CQRS (state)** — state-and-concurrency  
**Canonical Form** — invariants-and-correctness  
**Canonical Form Enforcement** — invariants-and-correctness  
**Cascade Failure** — state-and-concurrency  
**Catamorphism** — functions-and-composition  
**Cohesive** — design-principles  
**Combinator** — functions-and-composition  
**Commutative** — functions-and-composition  
**Complete (translator)** — translation-and-semantics  
**Composable** — functions-and-composition  
**Concolic Testing** — testing  
**Confluent** — invariants-and-correctness  
**Cons-list** — data-structures  
**Conservation Law** — invariants-and-correctness  
**Conservative** — invariants-and-correctness  
**Contract-First** — invariants-and-correctness  
**Coupled** — design-principles  
**Crash-only** — state-and-concurrency  
**Delta (state)** — state-and-concurrency  
**Delta Sourcing (state)** — state-and-concurrency  
**Dependency Injection** — design-principles  
**Deterministic** — functions-and-composition  
**Differential Testing** — testing  
**Divide and Conquer** — algorithms  
**Don't Repeat Yourself (DRY)** — design-principles  
**Duality** — design-principles  
**Dynamic Programming** — algorithms  
**Encapsulation** — design-principles  
**Equivalence Check** — testing  
**Event Sourcing** — state-and-concurrency  
**Factorization** — design-principles  
**Faithful** — translation-and-semantics  
**Finger Tree** — data-structures  
**Fixpoint** — invariants-and-correctness  
**Fork-join** — algorithms  
**Frame Condition** — invariants-and-correctness  
**Functorial** — type-systems  
**Fuzzing** — testing  
**Golden-file Test** — testing  
**Greedy** — algorithms  
**Hash Trie** — data-structures  
**Homomorphic** — functions-and-composition  
**Hylomorphism** — functions-and-composition  
**Idempotence** — functions-and-composition  
**Immutable** — state-and-concurrency  
**Information Hiding** — design-principles  
**Injective** — functions-and-composition  
**Interface Development** — methodology  
**Interface Segregation** — design-principles  
**Invariant** — invariants-and-correctness  
**Invariant Driven Development** — methodology  
**Inversion of Control (IoC)** — design-principles  
**Isomorphic** — functions-and-composition  
**Law of Demeter** — design-principles  
**Layer Architecture** — architecture  
**Layered Architecture** — architecture  
**Lensing Structure** — functions-and-composition  
**Linear (Data structure)** — data-structures  
**Lint Gate** — testing  
**Liskov Subsitution** — design-principles  
**Literate Programming** — methodology  
**Loop Invariant** — invariants-and-correctness  
**Lossless** — translation-and-semantics  
**Lost Update** — state-and-concurrency  
**Map-reduce** — algorithms  
**Memoized** — functions-and-composition  
**Mode Confusion** — translation-and-semantics  
**Model Checking** — testing  
**Monadic** — type-systems  
**Monotonic** — algorithms  
**Mutation Testing** — testing  
**Non-Injective Translation** — translation-and-semantics  
**Normalizing** — invariants-and-correctness  
**Open-closed** — design-principles  
**Optimistic Concurrency** — state-and-concurrency  
**Orthogonal** — design-principles  
**Over Generalization** — translation-and-semantics  
**Patch (state)** — state-and-concurrency  
**Persistent** — state-and-concurrency  
**Pessimistic Concurrency** — state-and-concurrency  
**Pipelined** — algorithms  
**Postcondition** — invariants-and-correctness  
**Precondition** — invariants-and-correctness  
**Product Type** — type-systems  
**Property Based Testing** — testing  
**Protocol First Design** — methodology  
**Provenance Tracking** — methodology  
**Pure** — functions-and-composition  
**Qualified** — translation-and-semantics  
**Reentrant** — state-and-concurrency  
**Refactoring** — design-principles  
**Referentially Transparent** — functions-and-composition  
**Reflection** — methodology  
**Refinement Calculus** — methodology  
**Replay (state)** — state-and-concurrency  
**Representation Invariant** — invariants-and-correctness  
**Round Trip Check** — testing  
**Round Trip Property** — testing  
**Round Trip Safe** — testing  
**Scaffolding** — methodology  
**Sentinel** — design-principles  
**Short-Circuit** — algorithms  
**Single Source of Truth (SSOT)** — design-principles  
**Sliding Window** — algorithms  
**Snapshot (state)** — state-and-concurrency  
**Snapshot + Log** — state-and-concurrency  
**Sound (translator)** — translation-and-semantics  
**Spaghettification** — design-principles  
**Specification-First** — methodology  
**Stable Dependency** — design-principles  
**State Desync** — translation-and-semantics  
**Stateful** — state-and-concurrency  
**Static Analysis** — invariants-and-correctness  
**Statified** — architecture  
**Streaming** — algorithms  
**Strict** — type-systems  
**Stub-real divergence** — translation-and-semantics  
**Surface-form leakage** — translation-and-semantics  
**Surjective** — functions-and-composition  
**Symbolic Execution** — testing  
**Tagged Union** — type-systems  
**Terminating** — state-and-concurrency  
**Test Driven Development** — methodology  
**Thundering Herd** — state-and-concurrency  
**Time of check time of use (TOCTOU)** — state-and-concurrency  
**Topological Sort** — algorithms  
**Total** — type-systems  
**Tracing** — algorithms  
**Translation Gap** — translation-and-semantics  
**Trie** — data-structures  
**Two Pointer** — algorithms  
**Type Invariant** — type-systems  
**Type-driven Development** — methodology  
**Under Specified Dispatch** — translation-and-semantics  
**Zipper** — data-structures
