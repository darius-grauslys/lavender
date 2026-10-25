# Module Review Guide

## Overview
This guide explains how module reviews are tracked and documented in the Lavender project.

## File Structure
- **Review Files**:
  - Location: `./agents/core/review/[module-path]/[module-name].md`
  - Example: `./agents/core/review/core-include/game.h.md`

## Review Process

### 1. Select Module
- Pick the next PENDING module from `modules_to_review.md`

### 2. Read and Analyze
- Read the `.h` file thoroughly
- Identify all function declarations and their purposes
- Check for proper documentation and correctness

### 3. Create Review File
- Create review file at `./agents/core/review/[module-path]/[module-name].md`
- Start with STATUS: `STARTED`
- Document:
  - All functions found
  - Their purposes
  - Any issues or questions
  - Implementation notes

### 4. Mark Status
- **STARTED**: When you begin reviewing the file
- **PASS**: When review is complete and the module is semantically sound with no bugs
- **FAIL**: When issues are found that need fixing

### 5. Update Trackers
- Mark the module as PASS/FAIL in `modules_to_review.md`
- If PASS, add to `modules_reviewed.md`

## Review Checklist
- [ ] All functions properly documented
- [ ] Function signatures correct
- [ ] No logical errors in declarations
- [ ] Proper use of types and parameters
- [ ] Consistent naming conventions
- [ ] No missing or incorrect implementations

## Status Definitions
| Status | Meaning |
|--------|---------|
| **PENDING** | Module hasn't been reviewed yet |
| **STARTED** | Currently under review |
| **PASS** | Review complete - module is correct and bug-free |
| **FAIL** | Review complete - issues found that need fixing |

## Example Review File Format
```markdown
# Module: [module-name].h

## Overview
[Brief description of the module's purpose]

## Functions
| Function | Purpose | Status |
|----------|---------|--------|
| func_name() | Description | [PENDING/PASS/FAIL] |

## Issues
- [List any problems found]

## Notes
- [Additional observations]

## Overall Status: [PASS/FAIL]
```
