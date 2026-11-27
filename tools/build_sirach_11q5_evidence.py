#!/usr/bin/env python3
"""Extract Sirach 51 lines preserved inside the 11Q5 Great Psalms Scroll.

11Q5 remains catalogued as a Psalms scroll, not as a dedicated Sirach manuscript.
Only QDR lines with a Sirach parallel anchor are copied. The parallel is a
passage locator; it does not claim that the entire referenced verse survives.
"""
import json
import pathlib
import re

ROOT = pathlib.Path("app/src/main/assets")
SOURCE = ROOT / "dss/etcbc_transcriptions.jsonl"
OUT = ROOT / "corpus/sirach/11q5_sirach_51_lines.jsonl"
INDEX = ROOT / "corpus/sirach/11q5_sirach_51_index.json"


def main():
    if not SOURCE.exists():
        raise SystemExit("ETCBC/QDR DSS transcription source is missing")
    rows = []
    candidate_scrolls = set()
    candidate_sirach_refs = set()
    with SOURCE.open(encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            item = json.loads(raw)
            scroll_key = re.sub(r"[^a-z0-9]", "", str(item.get("scroll", "")).lower())
            if "11q" in scroll_key:
                candidate_scrolls.add(scroll_key)
            if scroll_key not in {"11q5", "11qpsa", "11qps"}:
                continue
            refs = item.get("parallel_references", [])
            candidate_sirach_refs.update(str(r) for r in refs if "sir" in str(r).lower())
            sirach_refs = [r for r in refs if re.search(r"Sir\w*\s*51[.,]", str(r), re.I)]
            fragment = str(item.get("fragment", "")).strip()
            fragment_numbers = re.findall(r"\d+", fragment)
            column_number = int(fragment_numbers[-1]) if fragment_numbers else None
            try:
                line_number = int(item.get("line", ""))
            except (TypeError, ValueError):
                line_number = None
            if column_number == 21 and line_number is not None and 11 <= line_number <= 17:
                published_range = "Sirach 51:13-20"
            elif column_number == 22 and line_number == 1:
                published_range = "Sirach 51:30 (first two words only)"
            else:
                published_range = None
            if not sirach_refs and not published_range:
                continue
            rows.append({
                "writing_id":"sirach",
                "witness_id":"11Q5",
                "manuscript_identity":"11QPs-a; Great Psalms Scroll",
                "fragment_or_column":fragment,
                "line":str(item.get("line", "")),
                "sirach_parallel_references":sirach_refs,
                "published_passage_range":published_range,
                "transcription_text":item.get("transcription_text", ""),
                "normalized_text":item.get("normalized_text", ""),
                "word_records":item.get("word_records", []),
                "source":item.get("source"),
                "source_revision":item.get("source_revision"),
                "source_file":item.get("source_file"),
                "license":item.get("license"),
                "attribution":item.get("attribution"),
                "source_coordinate":f"11Q5 column/fragment {fragment}, line {item.get('line', '')}",
                "text_status":"direct_Hebrew_manuscript_line_in_Psalms_scroll",
                "reconstruction_status":"preserved_line_only; no completion supplied",
                "warning":"11Q5 is a Psalms scroll containing a Sirach hymn passage; it is not a dedicated Sirach codex. Parallel anchors do not prove that every word of the referenced verse survives."
            })
    if not rows:
        raise SystemExit(f"No Sirach 51 lines found in 11Q5/11QPsa QDR data; candidate scroll IDs={sorted(candidate_scrolls)}, Sirach anchors={sorted(candidate_sirach_refs)}; refusing to invent lines")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as target:
        for row in rows:
            target.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    refs = sorted({r for row in rows for r in row["sirach_parallel_references"]})
    passage_ranges = sorted({row["published_passage_range"] for row in rows if row["published_passage_range"]})
    INDEX.write_text(json.dumps({
        "schema_version":1,
        "record_type":"sirach_51_direct_11q5_psalms_scroll_evidence",
        "witness_id":"11Q5",
        "manuscript_identity":"11QPs-a; Great Psalms Scroll",
        "line_records":len(rows),
        "sirach_parallel_references":refs,
        "published_passage_ranges":passage_ranges,
        "source_revision":rows[0]["source_revision"],
        "license":"CC BY-NC 4.0",
        "attribution":rows[0]["attribution"],
        "limitations":[
            "11Q5 is a Psalms scroll, not a dedicated Sirach manuscript.",
            "The preserved Sirach hymn is in column XXI, lines 11-17 (Sirach 51:13-20) and column XXII, line 1 (Sirach 51:30; first two words only in the published transcription).",
            "Only actual QDR lines with Sirach parallel anchors or the published column-and-line locators are included.",
            "No missing words or verses are supplied from another witness in this asset."
        ]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(rows)} direct 11Q5 Sirach parallel line records.")


if __name__ == "__main__":
    main()
