
import os
import time
import json
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import requests
from datetime import datetime

ACCESS_TOKEN = os.getenv("ZENODO_TOKEN", "YOUR_ACCESS_TOKEN_HERE")
RATE_LIMIT = int(os.getenv("ZENODO_RATE_LIMIT", "604800"))  # Default = 7 days in seconds
MAX_RETRIES = 3
RETRY_BACKOFF = [10, 30, 90]  # seconds

parser = argparse.ArgumentParser(description="Batch upload files to Zenodo with rate limiting.")
parser.add_argument('--rate-limit', type=int, help='Seconds to wait between uploads')
args = parser.parse_args()

if args.rate_limit:
    RATE_LIMIT = args.rate_limit

def readable(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    return f"{days}d {hours}h ({seconds}s)"

print(f"🕒 Upload rate limit: {readable(RATE_LIMIT)}")
print(f"🔁 Retry policy: {MAX_RETRIES} attempts with backoff {RETRY_BACKOFF}")

def try_request(func, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            response = func(*args, **kwargs)
            if response.status_code in [200, 201, 202]:
                return response
            else:
                print(f"⚠️ Attempt {attempt+1}: HTTP {response.status_code} — {response.text}")
        except Exception as e:
            print(f"❌ Exception on attempt {attempt+1}: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_BACKOFF[attempt])
    return None

def upload_file(metadata_path, file_path):
    headers = {"Content-Type": "application/json"}
    params = {'access_token': ACCESS_TOKEN}

    # Step 1: Create deposition
    r = try_request(requests.post, "https://zenodo.org/api/deposit/depositions",
                    params=params, json={}, headers=headers)
    if not r:
        return None
    deposition_id = r.json()['id']

    # Step 2: Upload file
    with open(file_path, "rb") as fp:
        files = {'file': (os.path.basename(file_path), fp)}
        r = try_request(requests.post, f"https://zenodo.org/api/deposit/depositions/{deposition_id}/files",
                        params=params, files=files)
        if not r:
            return None

    # Step 3: Attach metadata
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    data = {"metadata": metadata}
    r = try_request(requests.put, f"https://zenodo.org/api/deposit/depositions/{deposition_id}",
                    params=params, data=json.dumps(data), headers=headers)
    if not r:
        return None

    # Step 4: Publish
    r = try_request(requests.post, f"https://zenodo.org/api/deposit/depositions/{deposition_id}/actions/publish",
                    params=params)
    if not r:
        return None

    doi = r.json().get("doi", "")
    print(f"✅ Published {os.path.basename(file_path)} — DOI: {doi}")
    return doi

def main():
    folder = os.path.join(BASE_DIR, "metadata")
    pdfs = os.path.join(BASE_DIR, "pdf")
    uploaded = []

    for fname in os.listdir(folder):
        if not fname.endswith(".json"):
            continue
        basename = os.path.splitext(fname)[0].replace("_metadata", "")
        pdf_path = os.path.join(pdfs, basename + ".pdf")
        meta_path = os.path.join(folder, fname)

        if not os.path.exists(pdf_path):
            print(f"⚠️ Missing PDF for {fname}, skipping.")
            continue

        doi = upload_file(meta_path, pdf_path)
        uploaded.append((basename, doi or "FAILED", datetime.now().isoformat()))

        print(f"⏳ Waiting {readable(RATE_LIMIT)} before next upload...\n")
        time.sleep(RATE_LIMIT)

    print("📝 Upload session complete.")

if __name__ == "__main__":
    main()
