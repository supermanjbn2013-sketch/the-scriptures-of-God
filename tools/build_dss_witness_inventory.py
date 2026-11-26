#!/usr/bin/env python3
"""Build a full inventory of DSS scroll identifiers actually present in QDR.

Parallel references are kept distinct from direct manuscript identity: they
are concordance anchors, not proof that a scroll contains a complete verse or
that the cited book is its only content.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ASSETS = Path("app/src/main/assets")
DSS = ASSETS / "dss"
LINES = DSS / "etcbc_transcriptions.jsonl"
SCROLLS = DSS / "etcbc_scroll_index.json"
OUT = DSS / "dss_witness_inventory.json"

BOOKS = {
    "Gen":"genesis","Exod":"exodus","Lev":"leviticus","Num":"numbers","Deut":"deuteronomy",
    "Josh":"joshua","Judg":"judges","Ruth":"ruth","1Sam":"1_samuel","2Sam":"2_samuel",
    "1Kgs":"1_kings","2Kgs":"2_kings","1Chr":"1_chronicles","2Chr":"2_chronicles",
    "Ezra":"ezra","Neh":"nehemiah","Esth":"esther","Job":"job","Ps":"psalms",
    "Prov":"proverbs","Eccl":"ecclesiastes","Song":"song_of_songs","Isa":"isaiah",
    "Jer":"jeremiah","Lam":"lamentations","Ezek":"ezekiel","Dan":"daniel","Hos":"hosea",
    "Joel":"joel","Amos":"amos","Obad":"obadiah","Jonah":"jonah","Mic":"micah",
    "Nah":"nahum","Hab":"habakkuk","Zeph":"zephaniah","Hag":"haggai","Zech":"zechariah","Mal":"malachi"
}
DIRECT = {"1qisaa":"isaiah","arugleviticus":"leviticus","xjoshua":"joshua","xjudges":"judges"}

def normalize(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())

def main():
    if not LINES.exists() or not SCROLLS.exists():
        raise SystemExit("Run tools/import_etcbc_dss.py before building the DSS witness inventory.")
    scroll_stats = defaultdict(lambda: {"fragment_ids": set(), "line_count": 0, "parallel_refs": set(), "parallel_book_ids": set()})
    ref_pattern = re.compile(r"^([A-Za-z0-9]+)[. ]([0-9]+)[.:]([0-9]+)$")
    with LINES.open(encoding="utf-8") as source:
        for raw in source:
            if not raw.strip():
                continue
            row = json.loads(raw)
            scroll = row["scroll"]
            stat = scroll_stats[scroll]
            stat["fragment_ids"].add(row["fragment"])
            stat["line_count"] += 1
            refs = set(row.get("parallel_references", []))
            refs.update(w.get("parallel_reference", "") for w in row.get("word_records", []))
            for ref in refs:
                match = ref_pattern.match(str(ref).strip())
                if match and match.group(1) in BOOKS:
                    stat["parallel_refs"].add(str(ref).strip())
                    stat["parallel_book_ids"].add(BOOKS[match.group(1)])
    scroll_index = json.loads(SCROLLS.read_text(encoding="utf-8"))
    index_rows = {row["scroll"]: row for row in scroll_index.get("scrolls", [])}
    if set(scroll_stats) != set(index_rows):
        raise ValueError("Scroll identifiers in line data and scroll index do not match.")
    records = []
    for scroll in sorted(scroll_stats):
        stat = scroll_stats[scroll]
        indexed = index_rows[scroll]
        records.append({
            "id": "dss_" + normalize(scroll),
            "shelfmark": scroll,
            "corpus_part": indexed.get("corpus_part"),
            "fragment_count": indexed["fragment_count"],
            "line_count": stat["line_count"],
            "parallel_reference_count": len(stat["parallel_refs"]),
            "parallel_reference_writing_ids": sorted(stat["parallel_book_ids"]),
            "directly_identified_writing_ids": [DIRECT[normalize(scroll)]] if normalize(scroll) in DIRECT else [],
            "language": "not specified by this imported index",
            "transcription_asset": "dss/etcbc_transcriptions.jsonl",
            "source_revision": scroll_index["source_revision"],
            "license": scroll_index["license"],
            "evidence_policy": "Parallel-reference writing IDs are source-supplied concordance links only. They do not establish complete verse coverage or replace direct manuscript identification."
        })
    result = {
        "schema_version": 1,
        "record_type": "Imported DSS scroll witness inventory",
        "source": "ETCBC/CACCHT Dead Sea Scrolls transcriptions, Martin Abegg data distributed through QDR",
        "source_revision": scroll_index["source_revision"],
        "license": scroll_index["license"],
        "scroll_count": len(records),
        "total_fragment_count": sum(r["fragment_count"] for r in records),
        "total_line_count": sum(r["line_count"] for r in records),
        "records": records,
        "limitations": [
            "This inventory covers only scroll identifiers and lines in the pinned QDR export.",
            "A scroll identifier is not a complete manuscript description; material, palaeographic date, cave, and repository are not inferred when absent from the source data.",
            "Parallel references are concordance metadata and do not prove identical wording or complete verse survival.",
            "Direct manuscript identification is listed separately from parallel-reference associations."
        ]
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built DSS witness inventory: {len(records)} scroll identifiers, {result['total_fragment_count']} fragment records, {result['total_line_count']} transcription lines.")

if __name__ == "__main__":
    main()
