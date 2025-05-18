
import os
import json
import requests
import csv
from datetime import datetime
import pprint

# === USER SETTINGS ===
ACCESS_TOKEN = 'In5kflgERNolXn0kLDjOC1sKEA0Q4syeQ88THt7u6sFrmqr8Icw6DI1RTRBP'  # Replace with your Zenodo token
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(BASE_DIR, 'pdf')
METADATA_DIR = os.path.join(BASE_DIR, 'metadata')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'upload_preview_log.csv')
ZENODO_URL = 'https://zenodo.org/api/deposit/depositions'
params = {'access_token': ACCESS_TOKEN}
headers = {'Content-Type': 'application/json'}

# Ensure logs directory exists
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# Load existing log to skip already uploaded
existing_uploads = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, newline='', encoding='utf-8') as logfile:
        reader = csv.DictReader(logfile)
        for row in reader:
            existing_uploads.add(row['PDF Filename'])

# Function to validate metadata
def is_valid_metadata(metadata):
    required = ["title", "description", "creators", "doi", "keywords", "upload_type", "communities", "access_right", "license"]
    for field in required:
        if field not in metadata or not metadata[field]:
            return False
    if not isinstance(metadata["creators"], list) or not all("name" in c for c in metadata["creators"]):
        return False
    if not any(c.get("identifier") == "semanticsensors" for c in metadata["communities"]):
        return False
    return True

# Function to upload to Zenodo
def upload_to_zenodo(pdf_filename, metadata):
    try:
        r = requests.post(ZENODO_URL, params=params, json={}, headers=headers)
        r.raise_for_status()
        deposition_id = r.json()['id']

        # Upload PDF
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        with open(pdf_path, 'rb') as fp:
            files = {'file': (pdf_filename, fp)}
            r = requests.post(f"{ZENODO_URL}/{deposition_id}/files", params=params, files=files)
            r.raise_for_status()

        # Attach metadata
        payload = {'metadata': metadata}
        r = requests.put(f"{ZENODO_URL}/{deposition_id}", params=params, json=payload, headers=headers)
        r.raise_for_status()

        # Publish
        r = requests.post(f"{ZENODO_URL}/{deposition_id}/actions/publish", params=params)
        if r.status_code == 202:
            doi = r.json()['doi']
            print(f"✅ Published {pdf_filename} — DOI: {doi}")
            return ('Success', doi)
        else:
            return ('Failed to publish', '')
    except Exception as e:
        print(f"❌ Error uploading {pdf_filename}: {e}")
        return ('Error', str(e))

# Function to log upload result
def log_upload(pdf_filename, metadata_file, status, result):
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as logfile:
        writer = csv.writer(logfile)
        writer.writerow([datetime.now().isoformat(), pdf_filename, metadata_file, status, result])

# Initialize log with header if not present
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as logfile:
        writer = csv.writer(logfile)
        writer.writerow(["Timestamp", "PDF Filename", "Metadata File", "Status", "Result"])

# Process files
for filename in os.listdir(PDF_DIR):
    if not filename.endswith(".pdf") or filename in existing_uploads:
        continue

    base = os.path.splitext(filename)[0]
    metadata_file = f"{base}_metadata.json"
    metadata_path = os.path.join(METADATA_DIR, metadata_file)

    if not os.path.exists(metadata_path):
        print(f"⚠️ No metadata file for {filename}, skipping.")
        continue

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    if not is_valid_metadata(metadata):
        print(f"⚠️ Metadata for {filename} is invalid or incomplete, skipping.")
        log_upload(filename, metadata_file, 'Skipped', 'Invalid metadata')
        continue

    # Show metadata preview

    print("\nPreview Metadata:")

    pprint.pprint(metadata, sort_dicts=False)
    confirm = input("Upload this to Zenodo? (y/n/edit): ").strip().lower()

    if confirm == 'edit':
        print("✏️ Enter new metadata JSON below. (Press Enter twice to finish)")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        try:
            metadata = json.loads('\n'.join(lines))
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            log_upload(filename, metadata_file, 'Skipped', 'User edit error')
            continue

    if confirm == 'y':
        status, result = upload_to_zenodo(filename, metadata)
        log_upload(filename, metadata_file, status, result)
    else:
        print(f"⏭️ Skipped {filename}")
        log_upload(filename, metadata_file, 'Skipped', 'User declined')
