#!/usr/bin/env bash

# Parse triangle filter stats from log file
# Format: "Triangle filter stats: checked=N, rejected=M (X.X%)"
parse_triangle_stats() {
    local log_file="$1"
    local checked rejected rate
    
    checked=$(grep -oE 'checked=[0-9]+' "$log_file" 2>/dev/null | tail -1 | cut -d= -f2 || echo "0")
    rejected=$(grep -oE 'rejected=[0-9]+' "$log_file" 2>/dev/null | tail -1 | cut -d= -f2 || echo "0")
    rate=$(grep -oE '\([0-9.]+%\)' "$log_file" 2>/dev/null | tail -1 | tr -d '()%' || echo "N/A")
    
    echo "$checked $rejected $rate"
}
