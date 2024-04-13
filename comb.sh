#!/bin/bash

# Define the root directory to search and the output file
ROOT_DIR="./"
OUTPUT_FILE="out.txt"

# Check if the output file already exists and remove it to start fresh
if [ -f "$OUTPUT_FILE" ]; then
    rm "$OUTPUT_FILE"
fi

# Find all .ts files and append their path and contents to the output file
find "$ROOT_DIR" -type f -name "*" | while read -r file; do
    echo "Path: $file" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n" >> "$OUTPUT_FILE"
done

