#!/usr/bin/env python3
"""Build the Sirach 51 evidence asset from the pinned Qumran-Digital 11Q5 source.

The source lines are stored with exact transcription, editorial reference
anchors, column/display-line labels, source URL and CC BY-SA attribution.
No words are supplied from another witness.
"""
import json
import pathlib

ROOT = pathlib.Path("app/src/main/assets")
SOURCE = ROOT / "catalog/sirach_11q5_source_lines.jsonl"
OUT = ROOT / "corpus/sirach/11q5_sirach_51_lines.jsonl"
INDEX = ROOT / "corpus/sirach/11q5_sirach_51_index.json"
SOURCE_URL = "https://lexicon.qumran-digital.org/transcriptions/11Q5/2025-03-11/index.html"


def main():
    if not SOURCE.exists():
        raise SystemExit("Curated 11Q5 Sirach source-line file is missing")
    rows = []
    with SOURCE.open(encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            row = json.loads(raw)
            if row.get("writing_id") != "sirach" or row.get("witness_id") != "11Q5":
                raise SystemExit("Unexpected record in 11Q5 Sirach source-line file")
            if row.get("source_url") != SOURCE_URL or row.get("source_license") != "CC BY-SA 4.0":
                raise SystemExit("11Q5 source URL or license does not match the pinned source")
            if not row.get("text") or not row.get("qdr_display_line"):
                raise SystemExit("11Q5 source line lacks text or display-line coordinate")
            if row.get("reconstruction_status") != "preserved_text_only; no missing words supplied":
                raise SystemExit("11Q5 source line is incorrectly marked as reconstructed")
            rows.append(row)
    if len(rows) != 9:
        raise SystemExit(f"Expected 9 curated Sirach 51 source lines, found {len(rows)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as target:
        for row in rows:
            target.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    ranges = sorted({row["published_passage_range"] for row in rows})
    INDEX.write_text(json.dumps({
        "schema_version":1,
        "record_type":"sirach_51_direct_11q5_psalms_scroll_evidence",
        "witness_id":"11Q5",
        "manuscript_identity":"11QPs-a; Great Psalms Scroll",
        "line_records":len(rows),
        "published_passage_ranges":ranges,
        "source_url":SOURCE_URL,
        "source_version":"2025-03-11",
        "license":"CC BY-SA 4.0",
        "attribution":rows[0]["attribution"],
        "limitations":[
            "11Q5 is a Psalms scroll, not a dedicated Sirach manuscript.",
            "QDR display-line numbers are not asserted to be physical manuscript line numbers.",
            "QDR Sirach references are editorial parallel anchors, not manuscript text.",
            "The Sirach 51:30 entry preserves only the first two words; the remainder of the QDR line belongs to another composition.",
            "No missing words or verses are supplied from another witness in this asset."
        ]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(rows)} direct 11Q5 Sirach line records from the pinned QDR transcription.")


if __name__ == "__main__":
    main()
