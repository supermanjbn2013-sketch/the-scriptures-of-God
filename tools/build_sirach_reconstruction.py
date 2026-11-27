#!/usr/bin/env python3
"""Build a verse-aligned Sirach witness comparison and Hebrew restoration layer.

Kahana's 1912 Hebrew edition is retained as supplied. Bracketed passages are
editorial Hebrew retroversions where Hebrew manuscript text was absent.
Greek Swete and Syriac Peshitta are aligned as separate versional witnesses.
No Greek/Syriac text is mechanically translated into Hebrew by this script.
"""
import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path("app/src/main/assets")
GREEK = ROOT / "corpus/verses.jsonl"
KAHANA = ROOT / "corpus/sirach/kahana_1912_hebrew.jsonl"
SYRIAC = ROOT / "corpus/sirach/peshitta_syriac.jsonl"
Q2_INDEX = ROOT / "corpus/sirach/2q18_index.json"
OUT = ROOT / "corpus/sirach/reconstructed_hebrew_comparison.jsonl"
INDEX = ROOT / "corpus/sirach/reconstructed_hebrew_comparison_index.json"


def read_jsonl(path):
    if not path.exists():
        raise SystemExit(f"Missing required Sirach source layer: {path}")
    with path.open(encoding="utf-8") as stream:
        for raw in stream:
            if raw.strip():
                yield json.loads(raw)


def main():
    greek = {}
    for row in read_jsonl(GREEK):
        if row.get("book") == "Sirach" and row.get("language") == "grc":
            greek[row["ref"]] = row

    kahana = defaultdict(list)
    for row in read_jsonl(KAHANA):
        key = (int(row["chapter"]), int(row["verse_number"]))
        kahana[key].append(row)

    syriac = {}
    for row in read_jsonl(SYRIAC):
        syriac[row["ref"]] = row

    q2_index = json.loads(Q2_INDEX.read_text(encoding="utf-8")) if Q2_INDEX.exists() else {}
    keys = set(kahana)
    for ref in set(greek) | set(syriac):
        parts = ref.rsplit(" ", 1)[-1].split(":")
        if len(parts) == 2:
            try:
                keys.add((int(parts[0]), int(parts[1])))
            except ValueError:
                pass

    records = []
    stats = {
        "kahana_editorial_retroversion": 0,
        "kahana_manuscript_based_edition": 0,
        "kahana_multiple_readings": 0,
        "unresolved_hebrew_gap": 0,
        "with_greek": 0,
        "with_syriac": 0,
        "with_2q18_passage_locator": 0
    }
    for chapter, verse in sorted(keys):
        ref = f"Sirach {chapter}:{verse}"
        kh = sorted(kahana.get((chapter, verse), []), key=lambda x: x["verse_label"])
        gr = greek.get(ref)
        sy = syriac.get(ref)
        if len(kh) > 1:
            status = "kahana_multiple_readings_preserved"
            stats["kahana_multiple_readings"] += 1
        elif kh and kh[0]["editorial_status"] == "bracketed_hebrew_retroversion_from_greek_and_or_syriac":
            status = "editorial_hebrew_retroversion"
            stats["kahana_editorial_retroversion"] += 1
        elif kh:
            status = "kahana_manuscript_based_edition"
            stats["kahana_manuscript_based_edition"] += 1
        else:
            status = "unresolved_hebrew_gap"
            stats["unresolved_hebrew_gap"] += 1
        if gr:
            stats["with_greek"] += 1
        if sy:
            stats["with_syriac"] += 1
        q2_ranges = []
        if chapter == 6 and 14 <= verse <= 15:
            q2_ranges.append({"witness":"2Q18","fragment":"1","published_range":"Sirach 6:14-15","warning":"Fragmentary range locator; does not assert every word in this verse survives."})
        if chapter == 6 and 20 <= verse <= 31:
            q2_ranges.append({"witness":"2Q18","fragment":"2","published_range":"Sirach 6:20-31","warning":"Fragmentary range locator; does not assert every word in this verse survives."})
        if q2_ranges:
            stats["with_2q18_passage_locator"] += 1
        records.append({
            "writing_id":"sirach",
            "ref":ref,
            "chapter":chapter,
            "verse":verse,
            "hebrew_reading_status":status,
            "hebrew_text":kh[0]["text"] if len(kh)==1 else None,
            "hebrew_readings":[
                {
                    "verse_label":x["verse_label"],
                    "text":x["text"],
                    "editorial_status":x["editorial_status"],
                    "source_id":x["source_id"],
                    "source_url":x["source_url"],
                    "direct_manuscript_witness":False
                } for x in kh
            ],
            "greek_text":gr.get("text") if gr else None,
            "greek_source":{
                "source":gr.get("source"),
                "edition":gr.get("edition"),
                "source_reference":gr.get("source_reference"),
                "source_url":gr.get("source_url"),
                "witness_basis":gr.get("witness_basis")
            } if gr else None,
            "syriac_text":sy.get("text") if sy else None,
            "syriac_source":{
                "source":sy.get("source"),
                "edition":sy.get("edition"),
                "source_revision":sy.get("source_revision"),
                "source_url":sy.get("source_url"),
                "license":sy.get("license")
            } if sy else None,
            "hebrew_fragment_range_evidence":q2_ranges,
            "reconstruction_note":(
                "Kahana's bracketed Hebrew is an editorial retroversion, not surviving Hebrew manuscript text."
                if status == "editorial_hebrew_retroversion" else
                "Kahana's unbracketed Hebrew is retained as an edition based on manuscript evidence; no single manuscript is assigned without fragment-level verification."
                if status == "kahana_manuscript_based_edition" else
                "Multiple Kahana readings are preserved separately; no preferred reading is selected automatically."
                if status == "kahana_multiple_readings_preserved" else
                "No Hebrew reading is supplied by the imported Kahana transcription for this reference. Greek and/or Syriac parallels remain separate; the Hebrew gap is unresolved."
            ),
            "method":"Reference alignment only; no automatic retroversion or silent merging of Hebrew, Greek, and Syriac."
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as target:
        for row in records:
            target.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    summary = {
        "schema_version":1,
        "record_type":"sirach_verse_aligned_witness_comparison_and_hebrew_restoration_layer",
        "record_count":len(records),
        "sources":{
            "hebrew":"David Kahana 1912 edition; manuscript-based and bracketed editorial retroversion statuses kept distinct",
            "greek":"Swete Septuagint Greek edition; edited text, not a diplomatic codex transcription",
            "syriac":"ETCBC Syriac Corpus 0.92 Peshitta; preliminary Ben Sira text, CC BY-NC 4.0",
            "qumran":"2Q18 direct fragment lines are stored separately; only passage-range locators are linked here"
        },
        "statistics":stats,
        "unresolved_hebrew_references":[r["ref"] for r in records if r["hebrew_reading_status"]=="unresolved_hebrew_gap"],
        "limitations":[
            "This is a verse-aligned research layer, not a claim that one complete ancient Hebrew manuscript survives.",
            "Kahana's printed edition is not a diplomatic transcription of one manuscript.",
            "Bracketed Kahana passages are editorial Hebrew retroversions from ancient versions, not direct Hebrew witness readings.",
            "Greek and Syriac are retained in their own languages and are never mechanically translated back into Hebrew.",
            "The Qumran 2Q18 range links are locators only; line-level fragments remain in their separate asset.",
            "The online Kahana transcription is marked incomplete; missing online verses are not automatically ancient manuscript lacunae."
        ],
        "asset":"corpus/sirach/reconstructed_hebrew_comparison.jsonl"
    }
    INDEX.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(records)} aligned Sirach references: {stats}")


if __name__ == "__main__":
    main()
