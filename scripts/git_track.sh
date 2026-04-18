#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <file-pattern>" >&2
    echo "  Find local commits ahead of upstream with changed files matching <file-pattern>." >&2
    echo "  Example: $0 '*.c'" >&2
    exit 1
fi

PATTERN="$1"

# Verify we're in a git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "Error: not inside a git repository." >&2
    exit 1
fi

# Verify there is an upstream tracking branch
if ! git rev-parse --abbrev-ref '@{u}' &>/dev/null; then
    echo "Error: current branch has no upstream tracking branch set." >&2
    echo "  Set one with: git branch --set-upstream-to=<remote>/<branch>" >&2
    exit 1
fi

# Iterate over commits ahead of upstream (oldest first)
git log --reverse --format='%H' '@{u}..HEAD' | while read -r COMMIT_HASH; do
    # Get list of changed files in this commit
    CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r "$COMMIT_HASH")

    # Check if any changed file matches the pattern
    MATCHED=false
    while IFS= read -r FILE; do
        # shellcheck disable=SC2254
        case "$FILE" in
            $PATTERN)
                MATCHED=true
                break
                ;;
        esac
    done <<< "$CHANGED_FILES"

    if [ "$MATCHED" = true ]; then
        SHORT_HASH=$(git rev-parse --short "$COMMIT_HASH")
        SUBJECT=$(git log -1 --format='%s' "$COMMIT_HASH")
        echo "${SHORT_HASH} ${SUBJECT}"
    fi
done
