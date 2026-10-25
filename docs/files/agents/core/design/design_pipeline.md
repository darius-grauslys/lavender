# Design Analysis Pipeline

Mechanics of running the design pass. The checklist itself lives in `design_guide.md`.

## Analysis Unit

- **Primary unit**: A logical module represented by a `.h`/`.c` pair.
- **Module set construction**:
  - Collect all `.h` files in the target scope (e.g., `core/include/`, `core/source/`)
  - Collect all `.c` files in the target scope
  - Map each file to its stem (strip `.h` or `.c` extension)
  - Union the two stem sets to form a set of module identifiers
  - For each module identifier, map back to its concrete files:
    - `.h` only (header-only / inline modules)
    - `.c` only (implementation-only modules)
    - Both `.h` and `.c` (standard paired modules)
- **Exclusion rule**: Omit monolithic files like `defines.h` that contain struct
  definitions for many modules (see `verify.md`), or split them before analysis.
- **Analysis grain**: Process one module at a time, then validate cross-module
  relationships (dependency direction, cycles, blast radius) in a second pass.

## Pass Structure

To keep small models (e.g., 27B) focused, run the guide in ordered passes,
one design axis per pass:

1. **Classification** — guide §1 (layer + abstraction/policy role)
2. **Dependency structure** — guide §2, §3 (direction, IoC)
3. **Boundary quality** — guide §4, §5 (information hiding, cohesion)
4. **Runtime contracts** — guide §6, §7, §8, §9 (ownership, temporal, concurrency, errors)
5. **Stability** — guide §10 (cross-module pass; requires call-site data)

## Output Format

For each module analyzed, produce a report with:

1. **Module path**: `core/include/[path]/module.h` (+ `core/source/[path]/module.c` if exists)
2. **Module type**: Header-only / Paired / Implementation-only / Singleton
3. **Primary layer**: Platform / Foundation / Core / Domain / Application
4. **Role**: Abstraction / Policy / Mixed
5. **Scores** (0 = clean, 5 = severe), one per guide section 2–10
6. **Top 3 issues** identified
7. **Blast radius estimate**: Low / Medium / High
8. **Refinement recommendation**: One sentence on the most impactful improvement
