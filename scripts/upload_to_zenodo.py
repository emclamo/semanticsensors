
import os
import json
import requests

# === USER SETTINGS ===
ACCESS_TOKEN = 'ZnxCrfDjzXg9P9txXXuLbbyjaaACkWGJGB8PPf11iHIS9AwRdUuBIKTwg8RY'  # Replace with your actual Zenodo token
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(BASE_DIR, 'pdf')
METADATA_DIR = os.path.join(BASE_DIR, 'metadata')
ZENODO_URL = 'https://zenodo.org/api/deposit/depositions'
params = {'access_token': ACCESS_TOKEN}
headers = {'Content-Type': 'application/json'}

def upload_to_zenodo(pdf_filename, metadata_filename):
    # Step 1: Create empty draft
    r = requests.post(ZENODO_URL, params=params, json={}, headers=headers)
    if r.status_code != 201:
        raise Exception(f"Failed to create deposition: {r.text}")
    deposition_id = r.json()['id']

    # Step 2: Upload the PDF file
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    with open(pdf_path, 'rb') as fp:
        files = {'file': (pdf_filename, fp)}
        r = requests.post(f"{ZENODO_URL}/{deposition_id}/files", params=params, files=files)
        if r.status_code != 201:
            raise Exception(f"Failed to upload file: {r.text}")

    # Step 3: Add metadata
    metadata_path = os.path.join(METADATA_DIR, metadata_filename)
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    payload = {'metadata': metadata}
    r = requests.put(f"{ZENODO_URL}/{deposition_id}", params=params, data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        raise Exception(f"Failed to update metadata: {r.text}")

    # Step 4: Publish
    r = requests.post(f"{ZENODO_URL}/{deposition_id}/actions/publish", params=params)
    if r.status_code == 202:
        print(f"✅ Successfully published: {pdf_filename}")
        print(f"🔗 DOI: {r.json()['doi']}")
    else:
        raise Exception(f"Failed to publish: {r.text}")

# === EXAMPLE USAGE ===
if __name__ == '__main__':
    # Replace with actual files you want to test
    upload_to_zenodo('paper1.pdf', 'paper1_metadata.json')
