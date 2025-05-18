
import os
import json
import pandas as pd

# Directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
metadata_dir = os.path.join(base_dir, "metadata")
log_path = os.path.join(base_dir, "metadata_validation_log.csv")

# Required fields
required_fields = ["title", "description", "creators", "doi", "keywords", "upload_type", "communities", "access_right", "license"]

# Recognized licenses (partial list)
valid_licenses = {"cc-by-4.0", "cc0-1.0", "cc-by-nc-sa-4.0", "MIT", "Apache-2.0", "GPL-3.0"}

def validate_metadata(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return ["Invalid JSON format"]

    missing = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing.append(field)

    # Check creators
    if "creators" in data:
        if not isinstance(data["creators"], list) or not all("name" in c for c in data["creators"]):
            missing.append("valid creators")

    # Check community assignment
    if "communities" in data:
        if not any(c.get("identifier") == "semanticsensors" for c in data["communities"]):
            missing.append("semanticsensors community")

    # Check license validity
    if "license" in data and data["license"] not in valid_licenses:
        missing.append("unrecognized license")

    # Risky combination: open access without valid license
    if data.get("access_right") == "open" and not data.get("license"):
        missing.append("open access without license")

    return missing

# Validate each metadata file
results = []
for filename in os.listdir(metadata_dir):
    if filename.endswith("_metadata.json"):
        full_path = os.path.join(metadata_dir, filename)
        missing_fields = validate_metadata(full_path)
        status = "OK" if not missing_fields else f"Missing: {', '.join(missing_fields)}"
        results.append((filename, status))

# Output validation log
df = pd.DataFrame(results, columns=["Metadata File", "Validation Status"])
df.to_csv(log_path, index=False)
print(f"✅ Validation complete. See log: {log_path}")
