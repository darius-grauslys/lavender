#!/bin/bash

# Usage: ./cross_compare_c_modules.sh -p <prompt>
#
# Iterates over each file in scripts/test_analysis/, strips the
# "test_analysis_" prefix and ".analysis" suffix from the filename
# to derive a .c source module name, searches for it under
# $LAVENDER_DIR/core/source/, and invokes aider with both the
# analysis file and the source file as read-only files along with
# the provided prompt.
#
# Skips the file if a corresponding source module is not found.

PROMPT=""

while getopts "p:" opt; do
    case $opt in
        p)
            PROMPT="$OPTARG"
            ;;
        *)
            echo "Usage: $0 -p <prompt>"
            exit 1
            ;;
    esac
done

if [ -z "$PROMPT" ]; then
    echo "Usage: $0 -p <prompt>"
    exit 1
fi

if [ -z "$LAVENDER_DIR" ]; then
    echo "Error: LAVENDER_DIR environment variable is not set."
    exit 1
fi

CORE_SOURCE_DIR="${LAVENDER_DIR}/core/source"

if [ ! -d "$CORE_SOURCE_DIR" ]; then
    echo "Error: Core source directory '$CORE_SOURCE_DIR' not found."
    exit 1
fi

ANALYSIS_DIR="scripts/test_analysis"

if [ ! -d "$ANALYSIS_DIR" ]; then
    echo "Error: Analysis directory '$ANALYSIS_DIR' not found."
    exit 1
fi

for analysis_file in "$ANALYSIS_DIR"/*; do
    if [ ! -f "$analysis_file" ]; then
        echo "No files found in $ANALYSIS_DIR."
        exit 1
    fi

    # Extract just the filename without path
    base_name=$(basename "$analysis_file")

    # Remove "test_analysis_" prefix
    stripped_name="${base_name#test_analysis_}"

    # Remove ".analysis" suffix
    source_c_name="${stripped_name%.analysis}"

    # Search for the .c source file under $LAVENDER_DIR/core/source/
    source_c_file=$(find "$CORE_SOURCE_DIR" -name "$source_c_name" -type f | head -n 1)

    if [ -z "$source_c_file" ]; then
        echo "Warning: Source file '$source_c_name' not found under '$CORE_SOURCE_DIR'. Skipping '$analysis_file'."
        continue
    fi

    echo "Processing: $analysis_file -> $source_c_file"

    # Build the aider read arguments
    AIDER_READ_ARGS=()
    AIDER_READ_ARGS+=(--read "$analysis_file")
    AIDER_READ_ARGS+=(--read "$source_c_file")

    echo "Would invoke: aider ${AIDER_READ_ARGS[*]} --message \"$PROMPT\" --model openrouter/anthropic/claude-4.6-sonnet --architect"

    # aider \
    #     "${AIDER_READ_ARGS[@]}" \
    #     --message "$PROMPT" \
    #     --model openrouter/anthropic/claude-4.6-sonnet \
    #     --architect

done

echo "Done processing analysis files."
