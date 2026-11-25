#!/usr/bin/env python3
"""Download version-pinned Qumran-Digital transcription pages for offline reference.

The archived HTML preserves the source page's own manuscript transcription and
its separately displayed parallels. It is NOT parsed into the DSS line corpus.
"""
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.request

VERSION = "2026-10-06"
IDS = ("4Q26", "4Q27", "4Q31", "4Q47", "4Q53")
BASE = "https://lexicon.qumran-digital.org/transcriptions"
OUT = pathlib.Path("app/src/main/assets/dss/qumran_digital")
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = OUT / "source_manifest.json"
LICENSE = "CC BY-SA 4.0"
ATTRIBUTION = ("DFG-Projekt 465277421, Qumran-Digital: Text und Lexikon; "
               "based on earlier Qumran-Wörterbuch project and precursor text by Martin Abegg.")
records = []

def fetch(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "The-Scriptures-of-God-Archive/1.0",
        "Accept": "text/html,application/xhtml+xml"
    })
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = response.read()
                if response.status != 200:
                    raise RuntimeError(f"Unexpected HTTP status {response.status}: {url}")
                return data
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last = exc
            if attempt < 4:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Download failed: {url}: {last}")

for manuscript_id in IDS:
    url = f"{BASE}/{manuscript_id}/{VERSION}/index.html?v={VERSION}"
    data = fetch(url)
    html = data.decode("utf-8", errors="strict")
    if len(data) < 3000 or f"#{manuscript_id}" not in html and manuscript_id not in html:
        raise RuntimeError(f"Unexpected or incomplete source page for {manuscript_id}")
    if "CC-BY-SA 4.0" not in html and "CC BY-SA 4.0" not in html:
        raise RuntimeError(f"Expected CC BY-SA 4.0 notice not found in {manuscript_id} page")
    if "Copyright" not in html or "Qumran-Digital" not in html:
        raise RuntimeError(f"Source identity/copyright block missing for {manuscript_id}")
    path = OUT / f"{manuscript_id}.html"
    path.write_bytes(data)
    records.append({
        "manuscript_id": manuscript_id,
        "source_url": url,
        "version": VERSION,
        "offline_asset": f"dss/qumran_digital/{manuscript_id}.html",
        "byte_count": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "content_type": "archived source HTML; manuscript lines and comparison parallels remain as separate page elements"
    })
    print(f"Downloaded {manuscript_id}: {len(data)} bytes; SHA-256 {records[-1]['sha256']}")

manifest = {
    "schema_version": 1,
    "record_type": "version_pinned_qumran_digital_source_html_archive",
    "provider": "DFG-Projekt 465277421, Qumran-Digital: Text und Lexikon",
    "version": VERSION,
    "license": LICENSE,
    "attribution": ATTRIBUTION,
    "records": records,
    "limitations": [
        "This archive preserves the source HTML; it is not a line-level transcription importer.",
        "Manuscript transcription, manuscript parallels and biblical comparison texts must remain distinct.",
        "Digital display-line labels are not physical manuscript column/line coordinates.",
        "CC BY-SA 4.0 attribution and share-alike terms apply."
    ]
}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Archived {len(records)} Qumran-Digital transcription source pages.")
