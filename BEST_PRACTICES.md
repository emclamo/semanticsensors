# Best Practices for Zenodo Uploads (PAnalytics Project)

This document outlines common pitfalls and our solutions to streamline team participation.

## ✅ File Handling

- Place all PDFs in the `pdf/` folder (named by DOI, e.g. `10.1016:j.snb.2019.126822.pdf`)
- Use the CSV metadata wizard to prepare metadata (see `csv_to_json_metadata.py`)
- Metadata files go in `metadata/` and should be named with `_metadata.json` suffix

## 🚫 Common Barriers and Solutions

| Problem                          | Solution                                                                                                |
|----------------------------------|---------------------------------------------------------------------------------------------------------|
| Team members can't run scripts   | Use a drag-and-drop folder structure via Box; contact Community manager to request shared folder access |
| Metadata JSON too technical      | Use `csv_to_json_metadata.py` from spreadsheet input                                                    |
| Upload too frequent              | Default rate limit = 7 days between uploads                                                             |
| Duplicate DOIs cause errors      | Script checks DOI via Zenodo API before upload                                                          |
| Team forgets license/access info | CSV wizard and validator include license/access prompts                                                 |

## 🔁 Review Process

1. Team submits PDFs to shared `pdf/` folder
2. CSV metadata is converted by project lead
3. Script performs dry run, validates
4. If successful, pushes record to Zenodo community

---

Contributions welcome. Document maintained by project lead.