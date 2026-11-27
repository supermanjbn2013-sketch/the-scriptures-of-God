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
SINAITICUS = ROOT / "corpus/sirach/codex_sinaiticus_greek.jsonl"
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

    sinaiticus = {}
    for row in read_jsonl(SINAITICUS):
        sinaiticus[row["ref"]] = row

    q2_index = json.loads(Q2_INDEX.read_text(encoding="utf-8")) if Q2_INDEX.exists() else {}
    q2_lines_path = ROOT / "corpus/sirach/2q18_hebrew_lines.jsonl"
    q11_lines_path = ROOT / "corpus/sirach/11q5_sirach_51_lines.jsonl"
    q2_lines = list(read_jsonl(q2_lines_path)) if q2_lines_path.exists() else []
    q11_lines = list(read_jsonl(q11_lines_path)) if q11_lines_path.exists() else []

    def range_contains(passage_range, chapter, verse):
        if not passage_range:
            return False
        try:
            chapter_part, verse_part = passage_range.replace("Sirach ", "").split(":")
            if int(chapter_part) != chapter:
                return False
            first, last = verse_part.split("-") if "-" in verse_part else (verse_part, verse_part)
            first_match = __import__("re").match(r"\d+", first)
            last_match = __import__("re").match(r"\d+", last)
            if not first_match:
                return False
            first_number = int(first_match.group())
            last_number = int(last_match.group()) if last_match else first_number
            return first_number <= verse <= last_number
        except (ValueError, TypeError):
            return False

    keys = set(kahana)
    for ref in set(greek) | set(syriac) | set(sinaiticus):
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
        "kahana_retroversion_readings": 0,
        "no_kahana_text_in_current_import": 0,
        "with_greek": 0,
        "with_syriac": 0,
        "with_sinaiticus": 0,
        "with_hebrew_fragment_range_evidence": 0,
        "with_direct_2q18_line_evidence": 0,
        "with_direct_11q5_line_evidence": 0
    }
    for chapter, verse in sorted(keys):
        ref = f"Sirach {chapter}:{verse}"
        kh = sorted(kahana.get((chapter, verse), []), key=lambda x: x["verse_label"])
        gr = greek.get(ref)
        sy = syriac.get(ref)
        si = sinaiticus.get(ref)
        stats["kahana_retroversion_readings"] += sum(1 for item in kh if item["editorial_status"] in ("bracketed_hebrew_retroversion_from_greek_and_or_syriac", "kahana_edition_contains_bracketed_editorial_retroversion"))
        if len(kh) > 1:
            status = "kahana_multiple_readings_preserved"
            stats["kahana_multiple_readings"] += 1
        elif kh and kh[0]["editorial_status"] in ("bracketed_hebrew_retroversion_from_greek_and_or_syriac", "kahana_edition_contains_bracketed_editorial_retroversion"):
            status = "editorial_hebrew_retroversion"
            stats["kahana_editorial_retroversion"] += 1
        elif kh:
            status = "kahana_manuscript_based_edition"
            stats["kahana_manuscript_based_edition"] += 1
        else:
            status = "no_kahana_text_in_current_import"
            stats["no_kahana_text_in_current_import"] += 1
        if gr:
            stats["with_greek"] += 1
        if sy:
            stats["with_syriac"] += 1
        if si:
            stats["with_sinaiticus"] += 1
        q2_ranges = []
        if chapter == 6 and 14 <= verse <= 15:
            q2_ranges.append({"witness":"2Q18","fragment":"1","published_range":"Sirach 6:14-15","warning":"Fragmentary range locator; does not assert every word in this verse survives."})
        if chapter == 6 and 20 <= verse <= 31:
            q2_ranges.append({"witness":"2Q18","fragment":"2","published_range":"Sirach 6:20-31","warning":"Fragmentary range locator; does not assert every word in this verse survives."})
        if chapter == 51 and 13 <= verse <= 20:
            q2_ranges.append({"witness":"11Q5","manuscript_identity":"11QPs-a; Great Psalms Scroll","column_and_lines":"column XXI, lines 11-17","published_range":"Sirach 51:13-20","warning":"The Sirach hymn is preserved within a Psalms scroll; consult the separate line transcription and do not assume every word in each verse survives."})
        if chapter == 51 and verse == 30:
            q2_ranges.append({"witness":"11Q5","manuscript_identity":"11QPs-a; Great Psalms Scroll","column_and_lines":"column XXII, line 1","published_range":"Sirach 51:30","warning":"Only the first two words of Sirach 51:30 are preserved in the published transcription."})
        q2_line_evidence = [
            {
                "witness_id": item["witness_id"],
                "fragment": item["fragment"],
                "source_coordinate": item["source_coordinate"],
                "transcription_text": item["transcription_text"],
                "normalized_text": item["normalized_text"],
                "text_status": item["text_status"],
                "source_revision": item["source_revision"],
                "source_license": item["source_license"],
                "warning": item["warning"]
            }
            for item in q2_lines
            if range_contains(item.get("passage_range"), chapter, verse)
        ]
        q11_line_evidence = [
            {
                "witness_id": item["witness_id"],
                "manuscript_identity": item["manuscript_identity"],
                "column": item["column"],
                "qdr_display_line": item["qdr_display_line"],
                "text": item["text"],
                "editorial_parallel_references": item["editorial_parallel_references"],
                "published_passage_range": item["published_passage_range"],
                "reference_status": item["reference_status"],
                "source_url": item["source_url"],
                "source_license": item["source_license"],
                "reconstruction_status": item["reconstruction_status"],
                "warning": item["warning"]
            }
            for item in q11_lines
            if range_contains(item.get("published_passage_range"), chapter, verse)
        ]
        if q2_ranges:
            stats["with_hebrew_fragment_range_evidence"] += 1
        if q2_line_evidence:
            stats["with_direct_2q18_line_evidence"] += 1
        if q11_line_evidence:
            stats["with_direct_11q5_line_evidence"] += 1
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
            "sinaiticus_greek_text":si.get("text") if si else None,
            "sinaiticus_source":{
                "witness_id":si.get("witness_id"),
                "manuscript_id":si.get("manuscript_id"),
                "source_revision":si.get("source_revision"),
                "source_url":si.get("source_url"),
                "license":si.get("license"),
                "source_verse_marker":si.get("source_verse_marker"),
                "source_coordinates":si.get("source_coordinates"),
                "correction_readings":si.get("correction_readings"),
                "editorial_supplied_text":si.get("editorial_supplied_text"),
                "marginal_text":si.get("marginal_text"),
                "note_text":si.get("note_text"),
                "other_readings":si.get("other_readings"),
                "text_status":si.get("text_status"),
                "reconstruction_status":si.get("reconstruction_status")
            } if si else None,
            "hebrew_fragment_range_evidence":q2_ranges,
            "direct_2q18_line_evidence":q2_line_evidence,
            "direct_11q5_line_evidence":q11_line_evidence,
            "reconstruction_note":(
                "Kahana's bracketed Hebrew is an editorial retroversion, not surviving Hebrew manuscript text."
                if status == "editorial_hebrew_retroversion" else
                "Kahana's unbracketed Hebrew is retained as an edition based on manuscript evidence; no single manuscript is assigned without fragment-level verification."
                if status == "kahana_manuscript_based_edition" else
                "Multiple Kahana readings are preserved separately; no preferred reading is selected automatically."
                if status == "kahana_multiple_readings_preserved" else
                "No Kahana text is present for this reference in the current online transcription. This is an online source-coverage gap, not proof that no Hebrew manuscript text survives. Greek and/or Syriac parallels remain separate; no Hebrew wording is invented."
            ),
            "method":"Reference alignment only; no automatic retroversion or silent merging of Hebrew, Greek, and Syriac.",
            "alignment_caveat":"Chapter and verse labels are cross-reference anchors; different textual traditions may divide or number verses differently, so an aligned reference does not prove exact textual equivalence."
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
            "sinaiticus":"Codex Sinaiticus Project TEI v1.95; direct Greek manuscript transcription, CC BY-NC-SA 3.0",
            "qumran":"2Q18 and 11Q5 direct line evidence are stored separately; passage locators are linked here, with 11Q5 retained as a Psalms scroll"
        },
        "statistics":stats,
        "references_missing_from_current_kahana_import":[r["ref"] for r in records if r["hebrew_reading_status"]=="no_kahana_text_in_current_import"],
        "limitations":[
            "This is a verse-aligned research layer, not a claim that one complete ancient Hebrew manuscript survives.",
            "Kahana's printed edition is not a diplomatic transcription of one manuscript.",
            "Bracketed Kahana passages are editorial Hebrew retroversions from ancient versions, not direct Hebrew witness readings.",
            "Greek and Syriac are retained in their own languages and are never mechanically translated back into Hebrew.",
            "Direct 2Q18 and 11Q5 transcription lines are attached as separate evidence arrays to aligned passage records; their text is never merged into the Kahana Hebrew reading.",
            "QDR passage references remain editorial anchors; display-line numbers are not manuscript physical line numbers.",
            "The online Kahana transcription is marked incomplete; missing online verses are not automatically ancient manuscript lacunae.",
            "Codex Sinaiticus is a separate Greek manuscript witness; its text is not merged with Swete or the Syriac Peshitta."
        ],
        "asset":"corpus/sirach/reconstructed_hebrew_comparison.jsonl"
    }
    INDEX.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(records)} aligned Sirach references: {stats}")


if __name__ == "__main__":
    main()
