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


def load_fraudlogix(path):
    """Reads Fraudlogix CSV: ip,risk,datacenter,connection_type,proxy,vpn"""
    scores = {}
    with open(path, 'r') as f:
        for row in csv.DictReader(f):
            if row.get('ip'):
                scores[row['ip']] = row
    return scores


def country_code_to_flag(code):
    """Converts a 2-letter country code to a flag emoji."""
    if not code or len(code) != 2:
        return ''
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)


def classify_connection(score_row):
    """Returns 'DataCenter' if the datacenter flag is true, else 'Residential'."""
    if not score_row:
        return 'Residential'
    dc = str(score_row.get('datacenter', '')).strip().lower()
    if dc in ('true', '1', 'yes'):
        return 'DataCenter'
    return 'Residential'


def normalize_risk(risk):
    """Normalizes Fraudlogix risk labels to short display form."""
    if not risk:
        return 'NA'
    r = risk.strip().lower()
    return {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        'extreme': 'Extreme',
        'na': 'NA',
    }.get(r, risk)


def rename_config(link, ip, country_code, risk, connection):
    """Rewrites the #fragment of a config link to (FLAG-RISK-CONNECTION-IP)."""
    flag = country_code_to_flag(country_code)
    new_name = f"({flag}-{risk}-{connection}-{ip})"

    if '#' in link:
        base, _ = link.split('#', 1)
        return f"{base}#{new_name}"
    return f"{link}#{new_name}"


def main():
    results = load_results('output/working.json')
    countries = load_countries('output/countries.json')
    fraudlogix = load_fraudlogix('output/fraudlogix_scores.csv')

    final_lines = []
    summary = []

    for entry in results:
        ip = entry['ip']
        link = entry['link']
        cc = countries.get(ip, '')
        row = fraudlogix.get(ip, {})

        risk = normalize_risk(row.get('risk', 'NA'))
        connection = classify_connection(row)

        new_link = rename_config(link, ip, cc, risk, connection)
        final_lines.append(new_link)
        summary.append(f"{cc or '??'} | {risk:<6} | {connection:<11} | {ip}")

    with open('output/final.txt', 'w') as f:
        f.write('\n'.join(final_lines) + '\n')

    with open('output/final_base64.txt', 'w') as f:
        encoded = base64.b64encode('\n'.join(final_lines).encode()).decode()
        f.write(encoded)

    print(f"\n--- Processed {len(final_lines)} working configs ---")
    for line in summary[:20]:
        print(line)
    if len(summary) > 20:
        print(f"... and {len(summary) - 20} more.")


if __name__ == '__main__':
    main()
