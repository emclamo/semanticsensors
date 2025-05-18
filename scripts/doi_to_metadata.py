
import os
import json
import requests
import re
import pandas as pd

# Define directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_dir = os.path.join(base_dir, "pdf")
metadata_dir = os.path.join(base_dir, "metadata")
os.makedirs(metadata_dir, exist_ok=True)

# Initialize review log
review_data = []

# Regex to extract DOI from filename
doi_pattern = re.compile(r"^(10\.\d{4,9})[:_/](.+)\.pdf$", re.IGNORECASE)

def get_metadata_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('message', {})
    return None

def parse_authors(author_list):
    creators = []
    for a in author_list:
        name = ""
        if 'family' in a and 'given' in a:
            name = f"{a['family']}, {a['given']}"
        elif 'name' in a:
            name = a['name']
        if name:
            creator = {"name": name}
            if 'ORCID' in a:
                creator["orcid"] = a["ORCID"].replace("https://orcid.org/", "")
            creators.append(creator)
    return creators

def fallback_keywords(meta):
    keys = []
    for field in ['subject', 'container-title', 'publisher']:
        value = meta.get(field)
        if isinstance(value, list):
            keys.extend(value)
        elif isinstance(value, str):
            keys.append(value)
    return list(set(k.strip() for k in keys if isinstance(k, str)))

# Process each PDF
for filename in os.listdir(pdf_dir):
    if not filename.lower().endswith('.pdf'):
        continue

    match = doi_pattern.match(filename)
    if not match:
        review_data.append((filename, "", "", "", "Invalid DOI filename format"))
        continue

    doi = f"{match.group(1)}/{match.group(2)}"
    metadata = get_metadata_from_doi(doi)

    if metadata is None:
        review_data.append((filename, doi, "", "", "DOI lookup failed"))
        continue

    title = metadata.get("title", [""])[0].strip()
    description = metadata.get("abstract", "No abstract available.")
    authors = parse_authors(metadata.get("author", []))
    keywords = fallback_keywords(metadata)

    # Validation flags
    status_notes = []
    if not title:
        status_notes.append("Missing title")
    if not authors:
        status_notes.append("Missing authors")
    if not keywords:
        status_notes.append("Missing keywords")
    if not description:
        status_notes.append("Missing description")

    status = "OK" if not status_notes else "Warning: " + "; ".join(status_notes + (["Missing or open access without license"] if "access_right" in zenodo_metadata and zenodo_metadata["access_right"] == "open" and not zenodo_metadata.get("license") else []))

    zenodo_metadata = {
        "title": title,
        "upload_type": "publication",
        "description": description,
        "creators": authors,
        "doi": doi,
        "keywords": keywords,
        "communities": [{"identifier": "semanticsensors"}],
        "access_right": "restricted",
    "license": "cc-by-4.0"
    }

    # Save to JSON
    json_filename = os.path.splitext(filename)[0] + "_metadata.json"
    json_path = os.path.join(metadata_dir, json_filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(zenodo_metadata, f, indent=2)

    review_data.append((filename, doi, title, ", ".join(keywords), status))

# Export review summary to CSV
review_df = pd.DataFrame(review_data, columns=["Filename", "DOI", "Title", "Keywords", "Status"])
review_csv_path = os.path.join(base_dir, "metadata_review_log.csv")
review_df.to_csv(review_csv_path, index=False)
print(f"✅ Metadata updated. See review log: {review_csv_path}")
