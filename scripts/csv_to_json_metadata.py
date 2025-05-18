import csv
import json
import os
from datetime import datetime

# Input/output locations
CSV_INPUT = "../csv/metadata_input.csv"
OUTPUT_FOLDER = "../metadata"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def parse_creators(field):
    names = [name.strip() for name in field.split(';') if name.strip()]
    return [{"name": n} for n in names]

def main():
    with open(CSV_INPUT, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row.get("doi", "").strip()
            title = row.get("title", "").strip()
            creators_raw = row.get("creators", "").strip()
            description = row.get("description", "No description provided.").strip()
            keywords = [k.strip() for k in row.get("keywords", "").split(',') if k.strip()]
            license_id = row.get("license", "cc-by-4.0").strip()
            access_right = row.get("access_right", "open").strip()
            upload_type = row.get("upload_type", "publication").strip()

            if not doi or not title or not creators_raw:
                print(f"⚠️ Skipping row with missing required fields: {row}")
                continue

            creators = parse_creators(creators_raw)
            identifier_safe_doi = doi.replace("/", ":").replace(" ", "_")

            metadata = {
                "title": title,
                "upload_type": upload_type,
                "description": description,
                "creators": creators,
                "doi": doi,
                "keywords": keywords,
                "license": license_id,
                "access_right": access_right,
                "communities": [{"identifier": "semanticsensors"}]
            }

            out_path = os.path.join(OUTPUT_FOLDER, f"{identifier_safe_doi}_metadata.json")
            with open(out_path, "w", encoding="utf-8") as out:
                json.dump(metadata, out, indent=2)
                print(f"✅ Wrote {out_path}")

if __name__ == "__main__":
    main()