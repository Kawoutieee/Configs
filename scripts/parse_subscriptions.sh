#!/bin/bash
set -e

mkdir -p output
> output/configs.txt

if [ ! -f "subscriptions.txt" ]; then
  echo "Error: subscriptions.txt not found!"
  exit 1
fi

if [ ! -s "subscriptions.txt" ]; then
  echo "Error: subscriptions.txt is empty!"
  exit 1
fi

echo "Processing subscriptions..."

while IFS= read -r url; do
  # Skip blank lines and comments
  if [[ -z "$url" || "$url" == \#* ]]; then 
    continue
  fi

  echo "Fetching: $url"
  
  # Download content, ignore failure on single URL
  content=$(curl -sL "$url" || true)
  if [ -z "$content" ]; then 
    echo "  -> Empty or failed to fetch."
    continue
  fi

  # Detect if it's base64 encoded. If no common proxy protocol is found in plain text, assume base64.
  if ! echo "$content" | grep -qE "(vmess|vless|trojan|ss)://"; then
    echo "  -> Decoding base64..."
    content=$(echo "$content" | base64 -d 2>/dev/null || true)
  fi

  # Extract only lines starting with known protocols
  echo "$content" | grep -E "^(vmess|vless|trojan|ss)://" >> output/configs.txt || true

done < subscriptions.txt

# Deduplicate
if [ -s output/configs.txt ]; then
  sort -u output/configs.txt -o output/configs.txt
  echo "Extracted $(wc -l < output/configs.txt) unique configs."
else
  echo "No valid configs found across subscriptions."
fi
