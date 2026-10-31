import csv
import json
import base64


def load_results(path):
    with open(path, 'r') as f:
        return json.load(f)


def load_countries(path):
    with open(path, 'r') as f:
        return json.load(f)


def load_ipqs(path):
    """Reads IPQS CSV: ip,fraud_score,connection_type,proxy,vpn"""
    scores = {}
    with open(path, 'r') as f:
        for row in csv.DictReader(f):
            if row.get('ip'):
                scores[row['ip']] = row
    return scores


def country_code_to_flag(code):
    if not code or len(code) != 2:
        return ''
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)


def risk_level(score):
    """Maps numeric fraud_score to a short risk label."""
    if score is None or score == 'NA':
        return 'NA'
    try:
        s = int(score)
    except (TypeError, ValueError):
        return 'NA'
    if s < 30:
        return 'Low'
    if s < 60:
        return 'Medium'
    if s < 85:
        return 'High'
    return 'Critical'


def connection_type(ipqs_row):
    """Returns 'DataCenter' if connection_type is 'Data Center', else 'Residential'."""
    if not ipqs_row:
        return 'Residential'
    ct = (ipqs_row.get('connection_type') or '').strip().lower()
    if ct == 'data center':
        return 'DataCenter'
    return 'Residential'


def rename_config(link, ip, country_code, risk, connection):
    flag = country_code_to_flag(country_code)
    new_name = f"({flag}-{risk}-{connection}-{ip})"
    if '#' in link:
        base, _ = link.split('#', 1)
        return f"{base}#{new_name}"
    return f"{link}#{new_name}"


def main():
    results = load_results('output/working.json')
    countries = load_countries('output/countries.json')
    ipqs_data = load_ipqs('output/ipqs_scores.csv')

    final_lines = []
    summary = []

    for entry in results:
        ip = entry['ip']
        link = entry['link']
        cc = countries.get(ip, '')
        row = ipqs_data.get(ip, {})

        score = row.get('fraud_score', 'NA')
        risk = risk_level(score)
        conn = connection_type(row)

        new_link = rename_config(link, ip, cc, risk, conn)
        final_lines.append(new_link)
        summary.append(f"{cc or '??'} | {risk:<8} | {conn:<11} | {ip}")

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
