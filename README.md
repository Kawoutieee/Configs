# Proxy Config Checker & Fraud Scorer

An automated GitHub Actions pipeline that fetches proxy subscription URLs, tests them for validity, determines the real exit IP, appends geography and fraud score metadata to their names, and outputs clean subscription files.

## How It Works

1. Reads URLs from `subscriptions.txt`.
2. Downloads and decodes configurations (VLESS, VMess, Trojan, Shadowsocks).
3. Tests the configs via `xray-knife` to isolate working nodes and capture the true exit IP.
4. Looks up the country code via `ip-api.com` and the fraud score via `goscamalytics`.
5. Renames the node using the format `(FLAG-SCORE-IP)`, e.g., `(🇺🇸-45-1.2.3.4)`.
6. Generates `output/final.txt` and `output/final_base64.txt`.
7. Uploads the output as workflow artifacts and commits them back to the repository.

## Usage

### Adding Subscriptions
Add your subscription URLs to `subscriptions.txt`, one per line. You can use `#` to comment out links. 
```text
# Main Sub
[https://example.com/sub1](https://example.com/sub1)
[https://example.com/sub2_base64](https://example.com/sub2_base64)
