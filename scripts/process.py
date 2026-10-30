import csv
import json
import base64

def load_results(path):
    """Reads working.json produced by the extraction step."""
    with open(path, 'r') as f:
        return json.load(f)

def load_countries(path):
    """Loads IP -> country code mapping."""
    with open(path, 'r') as f:
        return json.load(f)

def load_fraud_scores(path):
    """Loads IP -> fraud score mapping from proxycheck.io output."""
    scores = {}
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('ip'):
                scores[row['ip']] = row.get('score', 'NA')
    return scores

def country_code_to_flag(code):
    """Converts a 2-letter country code to a flag emoji."""
    if not code or len(code) != 2:
        return ''
    # Unicode regional indicator symbols
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)

def rename_config(link, ip, country_code, score):
    """Rewrites the #fragment of a config link to (FLAG-SCORE-IP)."""
    flag = country_code_to_flag(country_code)
    new_name = f"({flag}-{score}-{ip})"

    # Split at the first '#' to replace the fragment safely
    if '#' in link:
        base, _ = link.split('#', 1)
        return f"{base}#{new_name}"
    else:
        return f"{link}#{new_name}"

def main():
    # Load data
    results = load_results('output/working.json')
    countries = load_countries('output/countries.json')
    fraud_scores = load_fraud_scores('output/fraud.csv')

    final_lines = []
    summary = []

    for entry in results:
        ip = entry['ip']
        link = entry['link']
        cc = countries.get(ip, '')
        score = fraud_scores.get(ip, 'NA')

        new_link = rename_config(link, ip, cc, score)
        final_lines.append(new_link)
        summary.append(f"{cc or '??'} | {score:>3} | {ip}")

    # Write final plain text
    with open('output/final.txt', 'w') as f:
        f.write('\n'.join(final_lines) + '\n')

    # Write base64-encoded version
    with open('output/final_base64.txt', 'w') as f:
        encoded = base64.b64encode('\n'.join(final_lines).encode()).decode()
        f.write(encoded)

    # Print summary
    print(f"\n--- Processed {len(final_lines)} working configs ---")
    for line in summary[:20]:  # Show first 20 for brevity
        print(line)
    if len(summary) > 20:
        print(f"... and {len(summary) - 20} more.")

if __name__ == '__main__':
    main()
