#!/usr/bin/env python3
"""Extract verse-keyed Codex Sinaiticus Greek Ben Sira text from the pinned TEI page archive.

This is a separate manuscript witness. It is not merged with Swete, Kahana,
the Syriac Peshitta, or any Hebrew manuscript. The page/column/line coordinates
from the Sinaiticus TEI transcription are retained for every verse.
"""
import gzip
import json
import pathlib
import re
import xml.etree.ElementTree as ET
from collections import OrderedDict

ROOT = pathlib.Path("app/src/main/assets")
SIN = ROOT / "sinaiticus"
INDEX = SIN / "sinaiticus_index.json"
OUT = ROOT / "corpus/sirach/codex_sinaiticus_greek.jsonl"
OUT_INDEX = ROOT / "corpus/sirach/codex_sinaiticus_greek_index.json"
SOURCE_REVISION = "af1633b5102cbe6200e79053cc618ac447e1bb16"
SOURCE_URL = "https://github.com/itsee-birmingham/codex-sinaiticus"
LICENSE = "CC BY-NC-SA 3.0 Unported"
ATTRIBUTION = "Codex Sinaiticus Project electronic transcription; XML maintained by ITSEE, University of Birmingham."

def numeric(value):
    match = re.search(r"\d+", str(value or ""))
    return int(match.group()) if match else None

def context_value(context, element, attr):
    for item in context:
        if item.get("element") == element:
            attrs = item.get("attributes", {})
            if attrs.get(attr):
                return attrs[attr]
    return None

def verse_number(marker, chapter):
    value = str(marker or "")
    numbers = re.findall(r"\d+", value)
    if not numbers:
        return None
    if len(numbers) >= 2 and int(numbers[-2]) == chapter:
        return int(numbers[-1])
    return int(numbers[-1])

def is_sirach(label):
    normalized = re.sub(r"[^a-z]", "", str(label or "").lower())
    return "sirach" in normalized or "ecclesiastic" in normalized or "ecclus" in normalized or normalized == "sir"

def main():
    if not INDEX.exists():
        raise SystemExit("Codex Sinaiticus page index is missing; run the pinned TEI importer first.")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    if index.get("source_revision") != SOURCE_REVISION:
        raise SystemExit("Codex Sinaiticus source revision differs from the pinned manuscript transcription.")
    records = OrderedDict()
    book_labels = set()
    unmatched_sirach_markers = 0

    for page in index.get("pages", []):
        path = ROOT / page["asset_file"]
        if not path.exists():
            raise SystemExit(f"Missing Sinaiticus page asset: {path}")
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for raw in stream:
                if not raw.strip():
                    continue
                line = json.loads(raw)
                for token in line.get("token_markup", []):
                    context = token.get("context", [])
                    book_label = context_value(context, "div", "n")
                    book_entries = [
                        item for item in context
                        if item.get("element") == "div"
                        and item.get("attributes", {}).get("type") == "book"
                    ]
                    if book_entries:
                        book_attrs = book_entries[-1].get("attributes", {})
                        book_candidates = [
                            book_attrs.get("n"),
                            book_attrs.get("id"),
                            book_attrs.get("{http://www.w3.org/XML/1998/namespace}id")
                        ]
                        book_label = next((value for value in book_candidates if is_sirach(value)), book_candidates[0] or book_candidates[1] or book_label)
                    if not is_sirach(book_label):
                        for item in context:
                            attrs = item.get("attributes", {})
                            candidate = attrs.get("n") or attrs.get("id") or attrs.get("{http://www.w3.org/XML/1998/namespace}id")
                            if is_sirach(candidate):
                                book_label = candidate
                                break
                    if book_label:
                        book_labels.add(str(book_label))
                    if not is_sirach(book_label):
                        continue

                    chapter_entries = [
                        item for item in context
                        if item.get("element") == "div"
                        and item.get("attributes", {}).get("type") == "chapter"
                    ]
                    verse_entries = [item for item in context if item.get("element") == "ab"]
                    if not chapter_entries or not verse_entries:
                        unmatched_sirach_markers += 1
                        continue
                    chapter_value = chapter_entries[-1].get("attributes", {}).get("n")
                    chapter = numeric(chapter_value)
                    verse_attrs = verse_entries[-1].get("attributes", {})
                    verse_marker = verse_attrs.get("id") or verse_attrs.get("n")
                    if chapter is None:
                        unmatched_sirach_markers += 1
                        continue
                    verse = verse_number(verse_marker, chapter)
                    if verse is None:
                        unmatched_sirach_markers += 1
                        continue
                    try:
                        token_root = ET.fromstring(token.get("xml", ""))
                        token_text = "".join(token_root.itertext())
                    except ET.ParseError:
                        token_text = ""
                    if not token_text:
                        continue

                    ref = f"Sirach {chapter}:{verse}"
                    row = records.setdefault(ref, {
                        "writing_id": "sirach",
                        "ref": ref,
                        "chapter": chapter,
                        "verse": verse,
                        "language": "grc",
                        "text": [],
                        "correction_readings": [],
                        "editorial_supplied_text": [],
                        "marginal_text": [],
                        "note_text": [],
                        "other_readings": [],
                        "witness_id": "Codex Sinaiticus",
                        "manuscript_id": "GA 01",
                        "source_verse_marker": verse_marker,
                        "source_coordinates": [],
                        "source": "Codex Sinaiticus Project electronic transcription",
                        "source_revision": SOURCE_REVISION,
                        "source_url": SOURCE_URL,
                        "license": LICENSE,
                        "attribution": ATTRIBUTION,
                        "text_status": "direct_Greek_manuscript_main_reading; corrections_and_editorial_supply_separate",
                        "reconstruction_status": "preserved_main_reading_only; no_missing_words_supplied"
                    })
                    coordinate = {
                        "page_id": line.get("page_id"),
                        "column_id": line.get("column_id"),
                        "line_id": line.get("line_id")
                    }
                    if coordinate not in row["source_coordinates"]:
                        row["source_coordinates"].append(coordinate)

                    context_elements = {item.get("element") for item in context}
                    reading_entries = [item for item in context if item.get("element") == "rdg"]
                    reading_attrs = reading_entries[-1].get("attributes", {}) if reading_entries else {}
                    reading_type = reading_attrs.get("type", "")
                    corrector = reading_attrs.get("n")
                    token_record = {
                        "text": token_text,
                        "reading_type": reading_type or None,
                        "corrector": corrector,
                        "coordinate": coordinate
                    }

                    if "margin" in context_elements:
                        row["marginal_text"].append(token_record)
                    elif "note" in context_elements:
                        row["note_text"].append(token_record)
                    elif "supplied" in context_elements:
                        row["editorial_supplied_text"].append(token_record)
                    elif reading_entries and reading_type == "corr":
                        row["correction_readings"].append(token_record)
                    elif reading_entries and reading_type != "main-corr":
                        row["other_readings"].append(token_record)
                    else:
                        row["text"].append(token_text)

    if not records:
        raise SystemExit(
            "No Codex Sinaiticus Sirach verses were extracted. "
            f"Book labels observed: {sorted(book_labels)}; unmatched Sirach tokens: {unmatched_sirach_markers}"
        )

    final_rows = []
    for row in records.values():
        row["text"] = " ".join(row["text"])
        final_rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as target:
        for row in final_rows:
            target.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    chapters = sorted({row["chapter"] for row in final_rows})
    OUT_INDEX.write_text(json.dumps({
        "schema_version": 1,
        "record_type": "codex_sinaiticus_greek_sirach_verse_transcription",
        "witness_id": "Codex Sinaiticus",
        "manuscript_id": "GA 01",
        "source_revision": SOURCE_REVISION,
        "source_url": SOURCE_URL,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "verse_record_count": len(final_rows),
        "chapter_count": len(chapters),
        "chapters": chapters,
        "book_labels_observed_in_TEI": sorted(book_labels),
        "sirach_tokens_without_chapter_or_verse_marker": unmatched_sirach_markers,
        "correction_token_count": sum(len(row["correction_readings"]) for row in final_rows),
        "editorial_supplied_token_count": sum(len(row["editorial_supplied_text"]) for row in final_rows),
        "marginal_token_count": sum(len(row["marginal_text"]) for row in final_rows),
        "note_token_count": sum(len(row["note_text"]) for row in final_rows),
        "other_reading_token_count": sum(len(row["other_readings"]) for row in final_rows),
        "verses_without_main_reading": [row["ref"] for row in final_rows if not row["text"]],
        "asset": "corpus/sirach/codex_sinaiticus_greek.jsonl",
        "limitations": [
            "This is the Greek text of one physical codex, not a Hebrew manuscript and not the Swete critical edition.",
            "Verse labels are mapped from the TEI book, chapter and verse containers; source page, column and line identifiers are retained.",
            "Only the main-corr/original reading is used as the base text. Corrector readings, editorial supplied text, marginal material and notes are stored separately.",
            "TEI supplied text is editorial reconstruction, not direct manuscript writing; it is never silently included in the base text.",
            "Only text actually present in the imported transcription is included; absent manuscript text is not filled.",
            "The upstream transcription is CC BY-NC-SA 3.0; non-commercial and share-alike conditions apply.",
            "Any uncertain verse mapping must be resolved against the TEI source and manuscript page before being treated as final."
        ]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Extracted {len(final_rows)} Codex Sinaiticus Greek Sirach verse records across {len(chapters)} chapters.")

if __name__ == "__main__":
    main()
