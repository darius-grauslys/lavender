#!/bin/bash

# Usage: ./digest_test_report.sh <input_file>

if [ -z "$1" ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' not found."
    exit 1
fi

# Create output directory if missing
mkdir -p test_report_digest

# Read through the input file line by line, tracking line numbers
TOTAL_LINES=$(wc -l < "$INPUT_FILE")
LINE_NUM=0

while IFS= read -r line; do
    LINE_NUM=$((LINE_NUM + 1))

    # Check if this line matches the pattern .c:[0-9]*:
    if echo "$line" | grep -qE '\.c:[0-9]+:'; then

        # Extract the file path: everything from the first '/' up to and including '.c'
        # The match is: first '/' through '.c' before ':[0-9]+:'
        file_path=$(echo "$line" | grep -oE '/[^[:space:]]*\.c' | head -n 1)

        if [ -z "$file_path" ]; then
            continue
        fi

        # Get the basename of the matched file path (e.g. test_suite_collisions_hitbox_context.c)
        base_name=$(basename "$file_path")

        # Remove extension to get base without .c
        base_no_ext="${base_name%.c}"

        # Compute subpattern: remove "test_suite_[a-zA-Z]*_" from the beginning of base_no_ext
        subpattern=$(echo "$base_no_ext" | sed -E 's/^test_suite_[a-zA-Z]*_//')

        # Output file in test_report_digest/
        output_file="test_report_digest/${base_name}"

        # If the output file doesn't exist yet, write the header comment
        if [ ! -f "$output_file" ]; then
            echo "# This test report file is related to ${subpattern}.h.spec.md" > "$output_file"
            echo "#" >> "$output_file"
        fi

        # Append the matching line
        echo "$line" >> "$output_file"

        # Append the next line (read it)
        if [ "$LINE_NUM" -lt "$TOTAL_LINES" ]; then
            IFS= read -r next_line
            LINE_NUM=$((LINE_NUM + 1))
            echo "$next_line" >> "$output_file"
        fi
    fi
done < "$INPUT_FILE"

echo "Done. Reports written to test_report_digest/"
