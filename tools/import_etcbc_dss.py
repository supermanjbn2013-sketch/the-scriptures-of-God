#!/usr/bin/env python3
"""Import line-level ETCBC/Abegg DSS transcriptions for offline reading and search.

Upstream data: Qumran Digital Reader structured export, derived from ETCBC/DSS.
Text license: CC BY-NC 4.0. Do not use in commercial distributions.
"""
import json
import urllib.request
from pathlib import Path

REV = "f54f38464e18409eed8286fe24dd24f88d4735dd"
BASE = f"https://raw.githubusercontent.com/evenderekh/QDR/{REV}/data/"
SOURCES = [
    ("biblical", "qdr.1.1.biblical.json"),
    ("non_biblical", "qdr.1.1.non_biblical.json"),
]
OUT = Path("app/src/main/assets/dss")
OUT.mkdir(parents=True, exist_ok=True)
data_path = OUT / "etcbc_transcriptions.jsonl"
index = {}
total = 0

with data_path.open("w", encoding="utf-8", newline="\n") as target:
    for corpus_part, filename in SOURCES:
        url = BASE + filename
        request = urllib.request.Request(url, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            source = json.loads(response.read().decode("utf-8"))
        for scroll in source:
            scroll_id = str(scroll.get("scroll", "")).strip()
            if not scroll_id:
                raise ValueError(f"Missing scroll identifier in {filename}")
            stats = index.setdefault(scroll_id, {"scroll": scroll_id, "corpus_part": corpus_part, "fragment_count": 0, "line_count": 0})
            stats["fragment_count"] += len(scroll.get("fragments", []))
            for fragment in scroll.get("fragments", []):
                fragment_id = str(fragment.get("id", "")).strip()
                if not fragment_id:
                    raise ValueError(f"Missing fragment identifier in {scroll_id}")
                for line in fragment.get("lines", []):
                    words = line.get("words", [])
                    # QDR word tuple: source token, diplomatic display form, lemma, morphology, part of speech, passage parallel.
                    diplomatic = [str(w[1]) for w in words if len(w) > 1 and str(w[1]).strip()]
                    normalized = [str(w[0]) for w in words if len(w) > 0 and str(w[0]).strip()]
                    refs = sorted({str(w[5]) for w in words if len(w) > 5 and str(w[5]).strip()})
                    if not diplomatic and not normalized:
                        continue
                    record = {
                        "scroll": scroll_id,
                        "corpus_part": corpus_part,
                        "fragment": fragment_id,
                        "line": str(line.get("n", "")),
                        "transcription_text": " ".join(diplomatic),
                        "normalized_text": " ".join(normalized),
                        "parallel_references": refs,
                        "word_records": [
                            {
                                "surface": str(w[0]) if len(w) > 0 else "",
                                "surface_full": str(w[1]) if len(w) > 1 else "",
                                "parallel_reference": str(w[5]).strip() if len(w) > 5 else "",
                                "word_index": word_index
                            }
                            for word_index, w in enumerate(words)
                            if len(w) > 5 and str(w[5]).strip() and len(w) > 1 and str(w[1]).strip()
                        ],
                        "source": "ETCBC/DSS (Martin Abegg transcriptions), distributed in QDR structured data",
                        "source_revision": REV,
                        "source_file": filename,
                        "license": "CC BY-NC 4.0",
                        "attribution": "Martin G. Abegg Jr.; ETCBC/CACCHT Dead Sea Scrolls corpus; QDR structured export. See https://github.com/ETCBC/dss and https://github.com/evenderekh/QDR"
                    }
                    target.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                    stats["line_count"] += 1
                    total += 1

if total < 10000:
    raise SystemExit(f"Import unexpectedly small: {total} lines")
for required in ("1QS", "1QM", "1QpHab", "1QH", "1QIsa"):
    if not any(required.lower() in scroll.lower() for scroll in index):
        raise SystemExit(f"Expected major witness missing: {required}")
index_doc = {
    "schema_version": 1,
    "record_type": "ETCBC/Abegg DSS line transcription index",
    "source_revision": REV,
    "license": "CC BY-NC 4.0",
    "attribution": "Martin G. Abegg Jr.; ETCBC/CACCHT Dead Sea Scrolls corpus; structured export distributed by Qumran Digital Reader (QDR).",
    "source_urls": ["https://github.com/ETCBC/dss", "https://github.com/evenderekh/QDR"],
    "commercial_use": "Not permitted without separate permission from the rights holder.",
    "total_line_records": total,
    "scrolls": sorted(index.values(), key=lambda x: x["scroll"])
}
(OUT / "etcbc_scroll_index.json").write_text(json.dumps(index_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Synchronize the manuscript catalogue with the actual imported line-level data.
# A title match alone is not sufficient: only exact normalized witness IDs count.
catalog_path = Path("app/src/main/assets/catalog/dead_sea_scrolls_register.json")
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
normalized_index = {}
for scroll_id, details in index.items():
    key = "".join(ch.lower() for ch in scroll_id if ch.isalnum())
    normalized_index[key] = details
aliases = {
    "1QIsa-a": ("1qisaa", "1qisa"),
    "1QpHab": ("1qphab",),
    "1QapGen": ("1q20", "1qapgen"),
    "1QS": ("1qs",),
    "11Q19": ("11q19",),
    "1QM": ("1qm",),
}
for record in catalog.get("records", []):
    matches = []
    for alias in aliases.get(record.get("id"), ()):
        if alias in normalized_index:
            matches.append(normalized_index[alias])
    if matches:
        matched = matches[0]
        record["status"] = "offline transcription imported; line-level text available"
        record["transcription_coverage"] = {
            "source": "ETCBC/CACCHT Dead Sea Scrolls corpus, Martin Abegg transcriptions distributed through QDR",
            "license": "CC BY-NC 4.0",
            "scroll_identifier": matched["scroll"],
            "fragment_count": matched["fragment_count"],
            "line_count": matched["line_count"],
            "offline_asset": "dss/etcbc_transcriptions.jsonl",
            "index_asset": "dss/etcbc_scroll_index.json",
            "source_revision": REV,
            "coverage_note": "Only line records present in the pinned source export are included. This is not a complete reconstruction of the manuscript; gaps and absent fragments remain absent."
        }
    else:
        record["status"] = "metadata catalogued; no matching line-level transcription in the imported dataset"
        record.pop("transcription_coverage", None)
catalog["catalog_policy"] = "Metadata records are distinguished from imported transcriptions. A transcription is marked available only when an exact normalized witness identifier and line-level records are present in the pinned ETCBC/QDR export. Dates are approximate institutional descriptions. Digital images remain at the rights holder's site."
catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Imported {total} line-level DSS records from {len(index)} scrolls (CC BY-NC 4.0).")
print("Synchronized Dead Sea Scrolls register with exact imported witness IDs.")
for record in catalog.get("records", []):
    coverage = record.get("transcription_coverage", {})
    if coverage:
        print(f"Featured DSS witness {record['id']}: {coverage['scroll_identifier']} — {coverage['fragment_count']} fragments, {coverage['line_count']} lines.")
    else:
        print(f"Featured DSS witness {record['id']}: no exact transcription match in this import.")
for title, witness_ids in (
    ("1 Enoch Aramaic", ("4Q201", "4Q202", "4Q204", "4Q205", "4Q206", "4Q207", "4Q208", "4Q209", "4Q210", "4Q211", "4Q212")),
    ("Jubilees Hebrew", ("4Q216", "4Q217", "4Q218", "4Q219", "4Q220", "4Q221", "4Q222", "4Q223_224", "4Q225"))
):
    for witness_id in witness_ids:
        details = index.get(witness_id)
        if details:
            print(f"{title} witness {witness_id}: {details['fragment_count']} fragments, {details['line_count']} lines.")
        else:
            print(f"{title} witness {witness_id}: no exact transcription match in this import.")
