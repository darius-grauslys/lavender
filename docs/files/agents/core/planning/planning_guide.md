# Planning Guide

This guide documents the format and requirements for producing planning files.
When creating a plan file, reference the terminology index at
`agents/terminologies/index.md` for consistent, direct language.

## File Location

Each plan lives at `agents/core/planning/[module-path]/incorrect_modules.md`,
mirroring the corresponding review file at `agents/core/review/[module-path]/incorrect_modules.md`.

## Planning Process

### 1. Read the Review File
- Read the `incorrect_modules.md` review file to understand which functions or
  modules were flagged as **Incorrect**.
- Each entry follows the format:
  ```
  -e ./[path/to/function.md]
  Correctness Verdict: Incorrect
  ```
  or simply:
  ```
  -e ./[path/to/function.md]
  **Incorrect**
  ```

### 2. Read Source Files (Read-Only)
- Read the corresponding `.h` / `.c` files in `./include` and `./source` to
  understand the implementation context.
- **Critical**: These reads are **read-only**. You must NOT modify any source
  file (`.h`, `.c`, etc.). Only create `.md` files in `./agents/core/planning/`.

### 3. Use Terminology
- Consult `./agents/terminologies/index.md` for precise, concise terminology.
- Use the terms from the appropriate category files to keep the document direct.
- This ensures plans use a shared vocabulary across the project.
- **Recommended terminology routing by defect type:**
  - **Boundary/Null/Overflow issues**: `invariants-and-correctness.md`
    (`Boundary Condition`, `Invariant`, `Precondition`, `Postcondition`,
    `Representation Invariant`, `Static Analysis`, `Conservative`)
  - **Naming mismatches / missing implementations**: `translation-and-semantics.md`
    (`Translation Gap`, `State Desync`, `Stub-real divergence`,
    `Surface-form leakage`, `Under Specified Dispatch`)
  - **Bit-level / type confusion bugs**: `translation-and-semantics.md`
    (`Aliasing Bug`, `Mode Confusion`, `Non-Injective Translation`)
  - **Coupling / shared state concerns**: `design-principles.md`
    (`Coupled`, `Single Source of Truth (SSOT)`, `Spaghettification`,
    `Information Hiding`, `Don't Repeat Yourself (DRY)`, `Sentinel`)
  - **Counter/allocation bugs**: `invariants-and-correctness.md`
    (`Conservation Law`, `State Desync`, `Representation Invariant`)
  - **Testing recommendations**: `testing.md`
    (`Property Based Testing`, `Round Trip Check`, `Equivalence Check`,
    `Fuzzing`, `Mutation Testing`, `Golden-file Test`)

## Format Checklist

Every plan file MUST address the following items. Keep the document concise
and direct.

### Header Template

Begin every plan file with a standardized header. This promotes consistent
provenance across all planning documents. While not strictly enforced,
including all header fields is strongly recommended.

```markdown
# Planning: [review_file_module_name] — Incorrect Modules

**Review source:** `agents/core/review/[path/to/review]/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/[module].h`
- `core/source/[module].c`
- `tests/.../[test_file].c` (if applicable)

---
```

### 1. Problem Identification
- A concise identification of the problem(s) identified for the software section
  under review.
- Reference each incorrect function/module that was flagged in the review file.
- State the core defect or semantic mismatch in one or two sentences per issue.

### 2. Impact Assessment
- Identify portions of `./include` and `./source` which rely on the identified
  incorrect behavior of the software section under review.
- Describe how correcting the broken behavior will invalidate assumptions
  coupled to the broken behavior.
- List affected callers, callees, or data structures that may require
  cascading changes.
- If the incorrect behavior is already being relied upon as a de facto
  contract, note this explicitly.

### 3. Resolution Assessment
- The actual plan to resolve the issue (likely a re-articulation of the review
  file's findings, but framed as a resolution path).
- Articulate the steps required to bring the implementation into alignment
  with its semantic intent.
- For each incorrect function, specify:
  - What needs to change in the implementation
  - Whether callers need updating
  - Whether tests or documentation need updating
- If the fix has broad blast radius, note whether a phased approach is needed.

### 4. Test Verification Checklist

Before finalizing the plan, survey the relevant test suite to determine
whether existing tests need updating or whether new tests are needed. Include
findings in the resolution assessment:

- **Search test files** for references to the incorrect functions/modules. If
  tests exist, note:
  - Whether they assert on correct behavior (pre-flag) or broken behavior
    (post-flag)
  - Whether the fix invalidates any existing assertions
  - Whether new test cases are needed for edge cases (e.g., boundary
    conditions, null inputs)
- **Use terminology-based test recommendations** from
  `agents/terminologies/testing.md` when proposing new tests:
  - `Property Based Testing` for invariant verification
  - `Round Trip Check` for stateful operations
  - `Equivalence Check` for behavior preservation
  - `Fuzzing` for boundary/edge case coverage
  - `Mutation Testing` for test suite quality assessment
- **Blast radius**: Summarize the test impact (Low/Medium/High) and whether a
  phased approach for test updates is needed.

### 5. Blast Radius Summary

Include a brief blast radius assessment:
- How many files would need changes?
- Are the changes behavior-preserving for current callers?
- Is a phased approach needed?
- Are there any de facto contracts that would be invalidated?

## Constraints

- **Do NOT enact the plan**: Creating a plan file is a planning activity, not
  an implementation activity. Only create `.md` files in `./agents/core/planning/`.
- **Read-only source access**: You may read `.h`/`.c` files in `./include` and
  `./source`, but you must NOT modify them.
- **Only modify the plan file**: The only file you should create or modify is
  the planning `.md` file at the corresponding path under `./agents/core/planning/`.
- **Use terminology**: Use terms from `./agents/terminologies/index.md` to keep
  documents direct and concise.

## Terminology Routing

The terminology index is located at `./agents/terminologies/index.md`. It
provides:

- A categorical table mapping each file to its topic and the terms it contains.
- An alphabetical listing of all terms with their source file.

Consult the appropriate category file for precise definitions of terms used in
your plan (e.g., `errors-and-correctness.md` for invariant-related terms,
`design-principles.md` for coupling concerns, `testing.md` for verification
strategies).
