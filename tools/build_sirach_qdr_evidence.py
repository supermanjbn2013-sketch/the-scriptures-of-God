#!/usr/bin/env python3
"""Extract the directly preserved 2Q18 Ben Sira lines from the QDR import.

The fragment-to-passage ranges come from the published identification of 2Q18:
fragment 1 = Sirach 6:14-15; fragment 2 = Sirach 6:20-31. The exact manuscript
line text remains independent of the Kahana edition and is never completed here.
"""
import json
import pathlib
import re

ROOT = pathlib.Path("app/src/main/assets")
SOURCE = ROOT / "dss/etcbc_transcriptions.jsonl"
OUT = ROOT / "corpus/sirach/2q18_hebrew_lines.jsonl"
INDEX = ROOT / "corpus/sirach/2q18_index.json"

PASSAGES = {1: "Sirach 6:14-15", 2: "Sirach 6:20-31"}


def fragment_number(value):
    numbers = re.findall(r"\\d+", str(value))
    return int(numbers[-1]) if numbers else None


def main():
    if not SOURCE.exists():
        raise SystemExit("ETCBC/QDR DSS transcription source is missing")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with SOURCE.open(encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            item = json.loads(raw)
            scroll = str(item.get("scroll", "")).strip().replace(" ", "").lower()
            if scroll not in {"2q18", "2qsir"}:
                continue
            fragment = str(item.get("fragment", "")).strip()
            number = fragment_number(fragment)
            rows.append({
                "writing_id": "sirach",
                "witness_id": "2Q18",
                "fragment": fragment,
                "line": str(item.get("line", "")),
                "passage_range": PASSAGES.get(number),
                "transcription_text": item.get("transcription_text", ""),
                "normalized_text": item.get("normalized_text", ""),
                "word_records": item.get("word_records", []),
                "source": item.get("source"),
                "source_revision": item.get("source_revision"),
                "source_file": item.get("source_file"),
                "source_license": item.get("license"),
                "attribution": item.get("attribution"),
                "source_coordinate": f"2Q18 fragment {fragment}, line {item.get('line', '')}",
                "text_status": "direct_fragment_transcription; damaged_and_editorially_restored_letters_follow_source_notation",
                "reconstruction_status": "not_reconstructed; preserved_line_only",
                "warning": "Do not fill lacunae within this line from another witness without a separately marked supplement."
            })
    if not rows:
        raise SystemExit("No 2Q18 lines found in the imported QDR corpus; refusing to fabricate a witness layer")
    with OUT.open("w", encoding="utf-8", newline="\\n") as target:
        for row in rows:
            target.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\\n")
    fragments = sorted({r["fragment"] for r in rows})
    mapped = sorted({r["passage_range"] for r in rows if r["passage_range"]})
    INDEX.write_text(json.dumps({
        "schema_version": 1,
        "record_type": "sirach_2q18_direct_hebrew_fragment_index",
        "witness_id": "2Q18",
        "line_records": len(rows),
        "fragments": fragments,
        "published_passage_ranges": mapped,
        "unmapped_fragment_ids": sorted({r["fragment"] for r in rows if not r["passage_range"]}),
        "source_revision": rows[0]["source_revision"],
        "license": "CC BY-NC 4.0",
        "attribution": rows[0]["attribution"],
        "limitations": [
            "Only line-level text actually present in the QDR transcription is imported.",
            "Fragment 1 is identified with Sirach 6:14-15 and fragment 2 with Sirach 6:20-31; individual damaged words remain as transcribed.",
            "A passage range is an identification aid, not proof that every word or verse in that range survives.",
            "No Kahana, Greek, or Syriac text is silently inserted into the manuscript line."
        ]
    }, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Imported {len(rows)} direct 2Q18 line records from {len(fragments)} fragment(s); mapped ranges: {mapped}")


if __name__ == "__main__":
    main()
