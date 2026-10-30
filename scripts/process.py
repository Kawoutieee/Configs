import csv
import json
import base64
import urllib.parse
import os
import sys

# Hardcoded dict as requested
FLAGS = {
    "US": "🇺🇸", "DE": "🇩🇪", "IR": "🇮🇷", "GB": "🇬🇧", "NL": "🇳🇱",
    "FR": "🇫🇷", "CA": "🇨🇦", "FI": "🇫🇮", "SE": "🇸🇪", "CH": "🇨🇭",
    "SG": "🇸🇬", "JP": "🇯🇵", "KR": "🇰🇷", "AU": "🇦🇺", "TR": "🇹🇷"
}

def get_flag(country_code):
    if not country_code:
        return "🏳️"
    cc = country_code.upper()
    if cc in FLAGS:
        return FLAGS[cc]
    # Fallback to Unicode regional indicator symbols for unlisted codes
    if len(cc) == 2:
        return chr(ord(cc[0]) + 127397) + chr(ord(cc[1]) + 127397)
    return "🏳️"

def find_column_index(headers, keywords):
    for idx, header in enumerate(headers):
        if any(k in header.lower() for k in keywords):
            return idx
    return -1

def main():
    if not os.path.exists("output/results.csv"):
        print("No results.csv found. Exiting gracefully.")
        open("output/final.txt", "w").close()
        open("output/final_base64.txt", "w").close()
        return

    # Load countries
    countries = {}
    if os.path.exists("output/countries.json"):
        with open("output/countries.json", "r", encoding="utf-8") as f:
            countries = json.load(f)

    # Load fraud scores
    fraud_scores = {}
    if os.path.exists("output/fraud.csv"):
        with open("output/fraud.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            ip_idx = find_column_index(headers, ["ip"])
            score_idx = find_column_index(headers, ["score"])
            
            if ip_idx != -1 and score_idx != -1:
                for row in reader:
                    if len(row) > max(ip_idx, score_idx):
                        fraud_scores[row[ip_idx].strip()] = row[score_idx].strip()

    # Process results and rewrite links
    final_links = []
    
    print(f"{'Config Prefix':<40} | {'IP':<15} | {'Country':<7} | {'Score':<5}")
    print("-" * 75)

    with open("output/results.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, [])
        
        link_idx = find_column_index(headers, ["link", "url", "config"])
        ip_idx = find_column_index(headers, ["ip", "address"])
        status_idx = find_column_index(headers, ["status", "state"])
        
        if link_idx == -1 or ip_idx == -1:
            print("Error: Could not identify 'link' or 'ip' columns in results.csv")
            sys.exit(0)

        for row in reader:
            if len(row) <= max(link_idx, ip_idx):
                continue
                
            link = row[link_idx].strip()
            ip = row[ip_idx].strip()
            
            # Optional: skip if status column exists and indicates failure
            if status_idx != -1 and len(row) > status_idx:
                status = row[status_idx].strip().lower()
                if "fail" in status or "error" in status or "timeout" in status:
                    continue
            
            if not link or not ip:
                continue

            cc = countries.get(ip, "UN")
            flag = get_flag(cc)
            score = fraud_scores.get(ip, "NA")
            
            # Parse link and modify fragment
            parsed = urllib.parse.urlparse(link)
            new_fragment = urllib.parse.quote(f"({flag}-{score}-{ip})")
            
            # Reconstruct URL (handling cases where urlunparse might mangle protocol slashes)
            new_link = link.split('#')[0] + "#" + new_fragment
            final_links.append(new_link)
            
            # Print summary row
            prefix = link[:37] + "..." if len(link) > 40 else link
            print(f"{prefix:<40} | {ip:<15} | {cc:<7} | {score:<5}")

    # Write output
    with open("output/final.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_links) + "\n")
        
    with open("output/final_base64.txt", "w", encoding="utf-8") as f:
        encoded = base64.b64encode("\n".join(final_links).encode("utf-8")).decode("utf-8")
        f.write(encoded + "\n")

if __name__ == "__main__":
    main()
