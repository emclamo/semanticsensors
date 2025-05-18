
import os
import requests
import pandas as pd
from datetime import datetime
from html import escape

ACCESS_TOKEN = 'ZnxCrfDjzXg9P9txXXuLbbyjaaACkWGJGB8PPf11iHIS9AwRdUuBIKTwg8RY'
ZENODO_URL = 'https://zenodo.org/api/deposit/depositions'
params = {'access_token': ACCESS_TOKEN}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_CSV = os.path.join(BASE_DIR, 'upload_dashboard.csv')
OUTPUT_HTML = os.path.join(BASE_DIR, 'upload_dashboard.html')

def fetch_depositions():
    records = []
    page = 1
    while True:
        r = requests.get(ZENODO_URL, params={**params, 'page': page, 'size': 100})
        if r.status_code != 200:
            print("❌ Error fetching depositions:", r.text)
            break
        data = r.json()
        if not data:
            break
        records.extend(data)
        page += 1
    return records

def process_records(records):
    data = []
    for rec in records:
        md = rec.get('metadata', {})
        data.append({
            "Title": md.get("title", ""),
            "DOI": rec.get("doi", ""),
            "License": md.get("license", ""),
            "Access Right": md.get("access_right", ""),
            "Upload Type": md.get("upload_type", ""),
            "Publication Date": md.get("publication_date", ""),
            "Created": rec.get("created", ""),
            "Modified": rec.get("modified", ""),
            "Zenodo Link": f"https://zenodo.org/record/{rec['id']}"
        })
    return pd.DataFrame(data)

def generate_html(df):
    timestamp = datetime.now().isoformat()
    html = [f"""<html>
<head>
<title>Zenodo Upload Dashboard</title>
<style>
body {{
    font-family: 'Segoe UI', sans-serif;
    background: radial-gradient(circle, #1f1f1f, #0d0d0d);
    color: #eee;
    padding: 20px;
}}
select {{
    margin: 10px;
    padding: 6px;
    background-color: #333;
    color: #fff;
    border: 1px solid #666;
    border-radius: 4px;
}}
table {{
    border-collapse: collapse;
    margin-top: 20px;
    width: 100%;
}}
th {{
    background-color: #444;
    color: #f0f0f0;
    padding: 8px;
}}
td {{
    background-color: #222;
    padding: 8px;
    border: 1px solid #444;
}}
tr:hover td {{
    background-color: #2a2a2a;
}}
td.access-open {{ color: #9fdb6b; font-weight: bold; }}
td.access-restricted {{ color: #f79c9c; font-weight: bold; }}
td.access-closed {{ color: #ff6666; font-weight: bold; }}
td.access-embargoed {{ color: #ffd580; font-weight: bold; }}
a {{
    color: #87cefa;
    font-weight: bold;
    text-decoration: none;
}}
a:hover {{
    text-decoration: underline;
}}
</style>
<script>
function filterTable() {{
    var typeFilter = document.getElementById("typeFilter").value.toLowerCase();
    var accessFilter = document.getElementById("accessFilter").value.toLowerCase();
    var rows = document.querySelectorAll("table tbody tr");
    rows.forEach(row => {{
        var type = row.getAttribute("data-type").toLowerCase();
        var access = row.getAttribute("data-access").toLowerCase();
        var show = (typeFilter === "all" || type === typeFilter) &&
                   (accessFilter === "all" || access === accessFilter);
        row.style.display = show ? "" : "none";
    }});
}}
</script>
</head>
<body>
<h1>Zenodo Upload Dashboard</h1>
<p>Last updated: {{timestamp}}</p>
<label for="typeFilter">Filter by Record Type:</label>
<select id="typeFilter" onchange="filterTable()">
  <option value="all">Show All</option>
  <option value="publication">Publication</option>
  <option value="dataset">Dataset</option>
  <option value="presentation">Presentation</option>
  <option value="software">Software</option>
</select>
<label for="accessFilter">Filter by Access Right:</label>
<select id="accessFilter" onchange="filterTable()">
  <option value="all">Show All</option>
  <option value="open">Open</option>
  <option value="restricted">Restricted</option>
  <option value="closed">Closed</option>
  <option value="embargoed">Embargoed</option>
</select>
<table><thead><tr>"""]
    for col in df.columns:
        html.append(f"<th>{{escape(col)}}</th>")
    html.append("</tr></thead><tbody>")
    for _, row in df.iterrows():
        access_class = f"access-{str(row['Access Right']).lower()}"
        row_attrs = f'data-type="{{row["Upload Type"]}}" data-access="{{row["Access Right"]}}"'
        html.append(f"<tr {{row_attrs}}>")
        for col in df.columns:
            val = escape(str(row[col]))
            if col == "Access Right":
                html.append(f"<td class='{{access_class}}'>{{val}}</td>")
            elif col == "Zenodo Link":
                val = f"<a href='{{val}}' target='_blank'>View</a>"
                html.append(f"<td>{{val}}</td>")
            else:
                html.append(f"<td>{{val}}</td>")
        html.append("</tr>")
    html.append("</tbody></table></body></html>")
    return "\n".join(html)

if __name__ == '__main__':
    print("🔍 Fetching Zenodo records...")
    records = fetch_depositions()
    df = process_records(records)
    print("💾 Writing CSV and HTML dashboards...")
    df.to_csv(OUTPUT_CSV, index=False)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(generate_html(df))
    print(f"✅ Done. CSV saved to {{OUTPUT_CSV}}")
    print(f"🌐 HTML dashboard saved to {{OUTPUT_HTML}}")
