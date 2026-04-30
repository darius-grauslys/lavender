#!/bin/bash
# perf_summary.sh — Summarize build performance metrics.
#
# SAFETY: This script ONLY reads/writes .csv files inside a
# build/*/performance-metrics/ directory. It refuses to operate
# on paths outside this structure.
#
# Input: CSV file with lines of "milliseconds,target,source"
# Output: Per-directory totals, top slowest modules, and total time.
#         Writes summary.csv alongside the input file.

set -euo pipefail

csv="$1"

# --- Safety checks ---

# Must be a .csv file
case "$csv" in
    *.csv) ;;
    *) echo "perf_summary: refusing non-.csv input: $csv" >&2; exit 1 ;;
esac

# Resolve to absolute path and verify it lives under a build/ directory
csv_real=$(realpath -m "$csv")
case "$csv_real" in
    */build/*/performance-metrics/*.csv) ;;
    *) echo "perf_summary: path must be under build/*/performance-metrics/: $csv_real" >&2; exit 1 ;;
esac

if [ ! -f "$csv" ]; then
    echo "perf_summary: no metrics file at $csv" >&2
    exit 1
fi

summary_dir=$(dirname "$csv_real")

# Verify summary_dir is the same performance-metrics directory
case "$summary_dir" in
    */build/*/performance-metrics) ;;
    *) echo "perf_summary: summary dir outside expected path: $summary_dir" >&2; exit 1 ;;
esac

# --- Analysis ---

echo ""
echo "=== Build Performance Metrics ==="
echo ""

# Total time (sum of all module times — wall-clock with parallelism is different)
total_ms=$(awk -F',' '{s+=$1} END {print s}' "$csv")
link_ms=$(grep ',LINK,' "$csv" | awk -F',' '{s+=$1} END {print s+0}')
compile_ms=$((total_ms - link_ms))

printf "  Compile (sum):  %d ms  (%.2f s)\n" "$compile_ms" "$(echo "scale=2; $compile_ms/1000" | bc)"
printf "  Link:           %d ms  (%.2f s)\n" "$link_ms" "$(echo "scale=2; $link_ms/1000" | bc)"
printf "  Total (sum):    %d ms  (%.2f s)\n" "$total_ms" "$(echo "scale=2; $total_ms/1000" | bc)"
echo ""

# Per-directory totals (excluding LINK)
echo "--- Per-Directory (compile time) ---"
grep -v ',LINK,' "$csv" | awk -F',' '{
    split($2, parts, "/");
    if (length(parts) > 1) {
        dir = parts[1];
        for (i=2; i<length(parts); i++) dir = dir "/" parts[i];
    } else {
        dir = "(root)";
    }
    ms[dir] += $1;
    count[dir]++;
}
END {
    n = asorti(ms, sorted);
    for (i=1; i<=n; i++) {
        d = sorted[i];
        printf "  %6d ms  (%3d files)  %s\n", ms[d], count[d], d;
    }
}' | sort -rn
echo ""

# Top 10 slowest modules
echo "--- Top 10 Slowest Modules ---"
grep -v ',LINK,' "$csv" | sort -t',' -k1 -rn | head -10 | awk -F',' '{
    printf "  %6d ms  %s\n", $1, $2
}'
echo ""

# Write machine-readable summary (only to the same safe directory)
{
    echo "compile_ms,$compile_ms"
    echo "link_ms,$link_ms"
    echo "total_ms,$total_ms"
} > "$summary_dir/summary.csv"

echo "Detailed metrics: $csv_real"
echo "Summary: $summary_dir/summary.csv"
