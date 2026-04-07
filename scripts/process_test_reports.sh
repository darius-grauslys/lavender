#!/bin/bash

# Usage: ./process_test_reports.sh <prompt>
#
# Iterates over each .report file in test_report_digest/, extracts the
# referenced spec file name from the first line, searches for it under
# $LAVENDER_DIR/docs/specs/, and invokes aider with the report and spec
# as read-only files along with the provided prompt.
#
# Additionally, derives the corresponding .c source file name from the
# spec name and searches for it under $LAVENDER_DIR/core/source/,
# including it as a read-only file in the aider invocation if found.

if [ -z "$1" ]; then
    echo "Usage: $0 <prompt>"
    exit 1
fi

PROMPT="$1"

if [ -z "$LAVENDER_DIR" ]; then
    echo "Error: LAVENDER_DIR environment variable is not set."
    exit 1
fi

SPECS_DIR="${LAVENDER_DIR}/docs/specs"

if [ ! -d "$SPECS_DIR" ]; then
    echo "Error: Specs directory '$SPECS_DIR' not found."
    exit 1
fi

CORE_SOURCE_DIR="${LAVENDER_DIR}/core/source"

if [ ! -d "$CORE_SOURCE_DIR" ]; then
    echo "Error: Core source directory '$CORE_SOURCE_DIR' not found."
    exit 1
fi

REPORT_DIR="test_report_digest"

if [ ! -d "$REPORT_DIR" ]; then
    echo "Error: Report directory '$REPORT_DIR' not found. Run digest_test_report.sh first."
    exit 1
fi

for report_file in "$REPORT_DIR"/*.report; do
    if [ ! -f "$report_file" ]; then
        echo "No .report files found in $REPORT_DIR."
        exit 1
    fi

    # Read the first line and extract the spec file name
    first_line=$(head -n 1 "$report_file")
    spec_name=$(echo "$first_line" | grep -oE '[^ ]+\.h\.spec\.md' | head -n 1)

    if [ -z "$spec_name" ]; then
        echo "Warning: Could not extract spec file name from '$report_file'. Skipping."
        continue
    fi

    # Search for the spec file under $LAVENDER_DIR/docs/specs/
    spec_file=$(find "$SPECS_DIR" -name "$spec_name" -type f | head -n 1)

    if [ -z "$spec_file" ]; then
        echo "Warning: Spec file '$spec_name' not found under '$SPECS_DIR'. Skipping '$report_file'."
        continue
    fi

    # Derive the .c source file name by stripping .h.spec.md and appending .c
    source_base_name=$(echo "$spec_name" | sed -E 's/\.h\.spec\.md$//')
    source_c_name="${source_base_name}.c"

    # Search for the .c source file under $LAVENDER_DIR/core/source/
    source_c_file=$(find "$CORE_SOURCE_DIR" -name "$source_c_name" -type f | head -n 1)

    # Build the aider read arguments
    AIDER_READ_ARGS=()
    AIDER_READ_ARGS+=(--read "$report_file")
    AIDER_READ_ARGS+=(--read "$spec_file")

    if [ -n "$source_c_file" ]; then
        echo "Processing: $report_file -> $spec_file + $source_c_file"
        AIDER_READ_ARGS+=(--read "$source_c_file")
    else
        echo "Warning: Source file '$source_c_name' not found under '$CORE_SOURCE_DIR'."
        echo "Processing: $report_file -> $spec_file (without source)"
    fi

    aider \
        "${AIDER_READ_ARGS[@]}" \
        --message "$PROMPT" \
        --model openrouter/anthropic/claude-4.6-sonnet

done

echo "Done processing test reports."
