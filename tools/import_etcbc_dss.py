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
print(f"Imported {total} line-level DSS records from {len(index)} scrolls (CC BY-NC 4.0).")
