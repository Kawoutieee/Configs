#!/bin/bash
set -e

INPUT_FILE="subscriptions.txt"
OUTPUT_FILE="output/configs.txt"

mkdir -p output
> "$OUTPUT_FILE" # Clear output file

if [ ! -f "$INPUT_FILE" ]; then
    echo "::error::subscriptions.txt not found!"
    exit 1
fi

while IFS= read -r url || [ -n "$url" ]; do
    # Skip blank lines and comments
    [[ -z "$url" || "$url" =~ ^# ]] && continue

    echo "Fetching: $url"
    body=$(curl -sL --max-time 30 "$url")

    # Check if the body is base64 encoded
    if echo "$body" | base64 -d >/dev/null 2>&1; then
        echo "$body" | base64 -d >> "$OUTPUT_FILE"
    else
        echo "$body" >> "$OUTPUT_FILE"
    fi
    # Ensure a newline separates entries
    echo "" >> "$OUTPUT_FILE"
done < "$INPUT_FILE"

# Deduplicate and remove blank lines
sort -u "$OUTPUT_FILE" | grep -v '^$' > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

echo "Parsed configs saved to $OUTPUT_FILE"
