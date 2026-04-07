#!/bin/bash

set -e

usage() {
    echo "Usage: $0 -s <spec_dir> -t <test_dir> -p <prompt>"
    echo ""
    echo "  -s  Directory path containing .h.spec.md files"
    echo "  -t  Directory path containing test_suite_*_<name>.c files"
    echo "  -p  Prompt to pass to aider via --message"
    exit 1
}

spec_dir=""
test_dir=""
prompt=""

while getopts "s:t:p:" opt; do
    case "$opt" in
        s) spec_dir="$OPTARG" ;;
        t) test_dir="$OPTARG" ;;
        p) prompt="$OPTARG" ;;
        *) usage ;;
    esac
done

if [ -z "$spec_dir" ] || [ -z "$test_dir" ] || [ -z "$prompt" ]; then
    echo "Error: All arguments -s, -t, and -p are required."
    usage
fi

if [ ! -d "$spec_dir" ]; then
    echo "Error: Spec directory does not exist: $spec_dir"
    exit 1
fi

if [ ! -d "$test_dir" ]; then
    echo "Error: Test directory does not exist: $test_dir"
    exit 1
fi

# Build a list of all test files sorted by filename length (shortest first).
# This ensures that when multiple files match a suffix pattern, the shortest
# (most exact) match is selected first, preventing e.g. "process" from
# pairing with "filesystem_process".
sorted_test_files=()
while IFS= read -r line; do
    # Each line is "<length> <filepath>"; extract the filepath.
    sorted_test_files+=("${line#* }")
done < <(
    for f in "$test_dir"/test_suite_*.c; do
        [ -e "$f" ] || continue
        bname="$(basename "$f")"
        echo "${#bname} $f"
    done | sort -n
)

found_any=false

for spec_file in "$spec_dir"/*.h.spec.md; do
    [ -e "$spec_file" ] || continue

    base_name="$(basename "$spec_file")"
    # Strip .h.spec.md to get the core name, e.g. "global_space"
    core_name="${base_name%.h.spec.md}"

    # The suffix we expect every matching test file's basename to end with
    expected_suffix="_${core_name}.c"

    # Search for a matching test file from the length-sorted list
    match=""
    for test_file in "${sorted_test_files[@]}"; do
        test_base="$(basename "$test_file")"
        # Verify the basename truly ends with _<core_name>.c so that
        # e.g. "process" does not falsely match "filesystem_process"
        case "$test_base" in
            *"$expected_suffix")
                match="$test_file"
                break
                ;;
        esac
    done

    if [ -n "$match" ]; then
        found_any=true
        echo "Match found: $spec_file <-> $match"
        # aider --no-auto-lint --read "$spec_file" --message "$prompt" "$match"
    else
        echo "No matching test file for: $spec_file"
    fi
done

if [ "$found_any" = false ]; then
    echo "No spec/test pairs were found."
fi
