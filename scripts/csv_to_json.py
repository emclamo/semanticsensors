
import csv
import json
import os

# Define paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, 'source_tables', 'metadata_input.csv')
output_dir = os.path.join(base_dir, 'metadata')

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read the CSV and generate JSON files
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        filename = row['filename']
        title = row['title']
        authors = row['authors']
        doi = row['doi']
        description = row['description']
        keywords = row['keywords']
        upload_type = row['upload_type']
        license_id = row['license'] if 'license' in row and row['license'].strip() else 'cc-by-4.0'
        access_right = row['access_right'] if 'access_right' in row and row['access_right'].strip() else 'restricted'
        community = row.get('communities', 'semanticsensors')

        creators = [{'name': name.strip()} for name in authors.split(';') if name.strip()]
        keywords_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]

        metadata = {
            'title': title,
            'upload_type': upload_type,
            'description': description,
            'creators': creators,
            'doi': doi,
            'keywords': keywords_list,
            'communities': [{'identifier': community}],
            'access_right': access_right,
            'license': license_id
        }

        json_filename = os.path.splitext(filename)[0] + '_metadata.json'
        json_path = os.path.join(output_dir, json_filename)

        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(metadata, jsonfile, indent=2)

        print(f'Generated {json_filename}')
