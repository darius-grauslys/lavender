# METHODOLOGY

## Review Methodology

When reviewing functions in the Lavender codebase:

1. **Semantic Analysis**: Determine what the function is *intended* to do based on its name, parameters, and the surrounding code context.
2. **Pre-conditions**: Identify all conditions that must hold before the function executes, including parameter constraints.
3. **Post-conditions**: Identify all conditions guaranteed after the function returns.
4. **Correctness Evaluation**: Compare the implementation against the semantic intent and pre/post-conditions. Does the implementation faithfully reflect the intended semantics?
5. **Side Effects**: Acknowledge all observable side effects. Do NOT trace callee sites.
6. **Scope**: Callee behavior external to the function is out of scope. The executive body is the only thing that matters.

### Initialization Semantics

In the Lavender game engine, **initialization is NOT RAII**. Initialization is not coupled with resource acquisition. Instead:

- "Initialization" means **cleaning up a struct to its initial conditions**.
- It is used to **remove elements from pools** — when a struct is "initialized," it is being cleared/reset to a default state so it can be returned to a free pool or reused.

When reviewing functions whose name contains "init", "initialize", "reset", or similar, explicitly note whether the function follows the Lavender pattern (struct cleanup for pool reuse) rather than a RAII pattern (resource setup).
