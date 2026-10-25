# Function Review Guide

This guide documents the format and checklist for producing function review files. 
See `agents/core/review/include/audio/audio_effect.h/initialize_audio_effect.md` for
guidance on a working example. Note your file may contain line numbers, use them to
find the function under review.

Be careful when reading ./core module files, they can be very large. Use grep and
read files in sections when possible.

## File Location

Each review lives in `agents/core/review/<category>/<source_file>.<function_name>.md`.

## Format Checklist

Every review MUST replace the .md file's prior content and address the following items:

### 1. Header
- **Function name**
- **File of origin** (e.g., `core/source/audio/audio_effect.c` — no line numbers)

### 2. Semantic
- A single-line or short summary describing what the function does at a high level.

### 3. Pre-conditions
- Numbered list of all conditions that must hold before the function executes.
- Identify each parameter's constraints (e.g., must be non-null, may be null, valid range, etc.).

### 4. Post-conditions
- Numbered list of all conditions guaranteed after the function returns.
- For mutating functions: describe the state of the modified object(s).
- For non-mutating functions: describe the return value or lack thereof.

### 5. Correctness Verdict
- A single verdict: `Correct` or `Incorrect`.

### 6. Semantic Alignment
- Does the implementation fulfill the semantic intent?
- For struct initializers: confirm all struct fields are assigned, no member is omitted, no reordering occurs.
- For computing functions: confirm the computation matches the semantic intent. If the implementation is bugged and does not do its intention, this is where you mention it. This is where a bug causes a semantic assumption to fail.

### 7. Implementation Correctness
Note this is different than semantic drift, this is where subtle generic programming bugs occur, e.g. off by one.
- Type compatibility: do parameter types match target field/function types exactly? Any implicit conversions or truncation?
- Undefined behavior: no broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
- Validation: is validation appropriate for the function's role, or is it the caller's responsibility?

### 8. Side Effects
- Explicitly state all side effects.
- For pure functions: "No side effects."
- For mutating functions: describe what is mutated and how.
- Do NOT trace callee sites (out of scope) — only describe the function's own observable effects.

## Lavender-Specific Semantics

### Initialization ≠ RAII

In the Lavender game engine, **initialization is NOT coupled with resource acquisition** (it is NOT RAII). The term "initialization" in Lavender means:

- **Cleaning up a struct to its initial conditions.**
- **Used to remove elements from pools** — when a struct is "initialized," it is being cleared/reset to a default state so it can be returned to a free pool or reused.

When reviewing functions whose name contains "init", "initialize", "reset", or similar, explicitly note whether the function:
- Sets default/initial values (Lavender-style initialization / pool cleanup), OR
- Performs resource setup (RAII-style, which is NOT the Lavender pattern).

This semantic distinction affects how pre/post-conditions and side effects are evaluated.
