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

found_any=false

for spec_file in "$spec_dir"/*.h.spec.md; do
    [ -e "$spec_file" ] || continue

    base_name="$(basename "$spec_file")"
    # Strip .h.spec.md to get the core name, e.g. "global_space"
    core_name="${base_name%.h.spec.md}"

    # Search for a matching test file: test_suite_*_<core_name>.c
    match=""
    for test_file in "$test_dir"/test_suite_*_"${core_name}".c; do
        [ -e "$test_file" ] || continue
        match="$test_file"
        break
    done

    if [ -n "$match" ]; then
        found_any=true
        echo "Match found: $spec_file <-> $match"
        aider --message "$prompt" "$spec_file" "$match"
    else
        echo "No matching test file for: $spec_file"
    fi
done

if [ "$found_any" = false ]; then
    echo "No spec/test pairs were found."
fi
