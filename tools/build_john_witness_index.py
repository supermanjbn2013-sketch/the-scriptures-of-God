#!/usr/bin/env python3
"""Build a verse-indexed, source-preserving collation view for John's Gospel.

This is a navigation/index layer over the separately imported witness records.
It does not reconstruct missing text, normalize spellings, select a preferred
reading, or declare variants resolved.
"""
import gzip
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ASSETS = pathlib.Path("app/src/main/assets")
OUT = ASSETS / "catalog/john_witness_index.json"
BOOK_RE = re.compile(r"B04K(\d+)V(\d+)")
SIN_BOOK_ID = "B-B36-36-JOHN"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if line:
                yield json.loads(line)


def add_text(target, witness, ch, verse, text, page, label="", notes=None, line=""):
    if not text:
        return
    key = (ch, verse)
    record = target.setdefault(key, {}).setdefault(witness, {
        "text_parts": [], "pages": [], "source_labels": [],
        "correction_notes": [], "line_ids": []
    })
    # A verse crossing a page boundary can be indexed on both pages.
    # Keep identical diplomatic text once, but retain every page coordinate.
    if text not in record["text_parts"]:
        record["text_parts"].append(text)
    for field, value in (("pages", page), ("source_labels", label), ("line_ids", line)):
        if value and value not in record[field]:
            record[field].append(value)
    for note in notes or []:
        if note and note not in record["correction_notes"]:
            record["correction_notes"].append(note)


def import_labelled_witness(witness, index_path, target):
    index = read_json(ASSETS / index_path)
    for page in index.get("pages", []):
        asset = ASSETS / page["asset_file"]
        for record in read_jsonl(asset):
            label = record.get("source_label", "")
            match = BOOK_RE.search(label)
            if not match:
                continue
            ch, verse = map(int, match.groups())
            add_text(
                target, witness, ch, verse, record.get("text", "").strip(),
                record.get("page_id") or page.get("page_id"), label,
                record.get("correction_notes", []),
                ",".join(record.get("line_ids", []))
            )
    return {
        "provider": index.get("provider", ""),
        "document_id": index.get("document_id"),
        "source_url": index.get("source_url", ""),
        "attribution": index.get("attribution", ""),
        "license": index.get("license", ""),
        "license_url": index.get("license_url", ""),
        "scope_note": index.get("scope_note", ""),
    }


def xml_text(fragment):
    try:
        root = ET.fromstring("<root>" + fragment + "</root>")
    except ET.ParseError:
        return re.sub(r"<[^>]+>", "", fragment).strip()

    def collect(node):
        tag = node.tag.rsplit("}", 1)[-1].lower()
        if tag in {"note", "pb", "cb", "lb", "seg"}:
            return ""
        value = node.text or ""
        for child in list(node):
            child_value = collect(child)
            if child.tag.rsplit("}", 1)[-1].lower() == "supplied" and child_value:
                child_value = "[" + child_value + "]"
            value += child_value + (child.tail or "")
        return value

    return " ".join(collect(root).split())


def import_sinaiticus(target):
    index = read_json(ASSETS / "sinaiticus/sinaiticus_index.json")
    for page in index.get("pages", []):
        asset = ASSETS / page["asset_file"]
        for record in read_jsonl(asset):
            for token in record.get("token_markup", []):
                book = None
                chapter = None
                verse = None
                for context in token.get("context", []):
                    element = context.get("element")
                    attrs = context.get("attributes", {})
                    if element == "div" and attrs.get("type") == "book":
                        book = attrs.get("{http://www.w3.org/XML/1998/namespace}id")
                    elif element == "div" and attrs.get("type") == "chapter":
                        raw_chapter = attrs.get("n", "")
                        if str(raw_chapter).isdigit():
                            chapter = int(raw_chapter)
                    elif element == "ab":
                        raw_verse = attrs.get("n", "")
                        if str(raw_verse).isdigit():
                            verse = int(raw_verse)
                if book != SIN_BOOK_ID or not chapter or not verse:
                    continue
                text = xml_text(token.get("xml", ""))
                if not text:
                    continue
                add_text(
                    target, "Sinaiticus", chapter, verse, text,
                    record.get("page_id") or page.get("page_id"), "",
                    [], record.get("line_id", "")
                )
    return {
        "provider": "Codex Sinaiticus Project / ITSEE",
        "source_url": "https://github.com/itsee-birmingham/codex-sinaiticus",
        "license": "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)",
        "scope_note": "Original manuscript transcription, indexed by book/chapter/verse context. Page, column, line, and token markup remain available in the separate Sinaiticus page archive."
    }


def main():
    indexed = {}
    metadata = {}
    sources = [
        ("P52", "papyri/p52/p52_index.json"),
        ("P66", "papyri/p66/p66_index.json"),
        ("P75", "papyri/p75/p75_index.json"),
        ("Vaticanus", "vaticanus/vaticanus_index.json"),
    ]
    for witness, index_path in sources:
        index_file = ASSETS / index_path
        if index_file.exists():
            metadata[witness] = import_labelled_witness(witness, index_path, indexed)
    sinaiticus_index = ASSETS / "sinaiticus/sinaiticus_index.json"
    if sinaiticus_index.exists():
        metadata["Sinaiticus"] = import_sinaiticus(indexed)

    verses = []
    counts = {witness: 0 for witness in metadata}
    priority_order = ["P52", "P66", "P75", "Vaticanus", "Sinaiticus"]
    for (chapter, verse), witness_records in sorted(indexed.items()):
        witnesses = {}
        for witness, record in witness_records.items():
            text_parts = record["text_parts"]
            witnesses[witness] = {
                "text": " ".join(text_parts),
                "pages": record["pages"],
                "source_labels": record["source_labels"],
                "line_ids": record["line_ids"],
                "correction_notes": record["correction_notes"],
            }
            counts[witness] = counts.get(witness, 0) + 1

        present = [name for name in priority_order if name in witnesses and witnesses[name]["text"].strip()]
        complete = [name for name in present if "[" not in witnesses[name]["text"] and "]" not in witnesses[name]["text"]]
        if complete:
            selected = complete[0]
            selection_status = "earliest_unbracketed_text"
        elif present:
            selected = present[0]
            selection_status = "earliest_available_text_contains_editorial_supply"
        else:
            selected = None
            selection_status = "no_witness_text"

        earlier_with_supply = []
        if selected:
            for name in present:
                if name == selected:
                    break
                if "[" in witnesses[name]["text"] or "]" in witnesses[name]["text"]:
                    earlier_with_supply.append(name)

        verses.append({
            "reference": f"John {chapter}:{verse}",
            "chapter": chapter,
            "verse": verse,
            "witnesses": witnesses,
            "priority_witness": selected,
            "priority_text": witnesses[selected]["text"] if selected else "",
            "priority_status": selection_status,
            "earlier_witnesses_with_editorial_supply": earlier_with_supply,
            "priority_note": "Verse-level selection aid: this is the earliest indexed witness reading without explicit square-bracket editorial supply. Absence of brackets does not prove that the whole verse survives; physical gaps and partial verses must still be checked against page, column, line, and facsimile evidence. Earlier witnesses containing editorial supply remain separately visible. This is not a completed collation or translation."
        })

    if len(verses) < 800 or not {"P66", "P75", "Vaticanus", "Sinaiticus"}.issubset(metadata):
        raise SystemExit(
            "John witness index rejected: insufficient imported witness coverage "
            f"({len(verses)} verses; witnesses={sorted(metadata)})"
        )

    output = {
        "schema_version": 1,
        "record_type": "john_verse_witness_index",
        "book": "John",
        "purpose": "Offline verse-level navigation across independently preserved Greek manuscript transcriptions.",
        "text_policy": "Diplomatic witness text is preserved as imported. A separate verse-level priority aid identifies the earliest indexed witness reading without explicit square-bracket editorial supply. Original witness records remain unchanged; this does not prove verse completeness or resolve variants. No spelling normalization, harmonization, reconstruction, or translation is performed.",
        "absence_policy": "No record for a witness at a verse does not by itself establish textual omission. Consult the page image and source transcription to distinguish physical loss, illegibility, omitted text, and indexing gaps.",
        "witness_priority_order": priority_order,
        "witness_metadata": metadata,
        "witness_verse_counts": counts,
        "verse_count": len(verses),
        "verses": verses,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Built John witness index:", len(verses), "verses;", counts)


if __name__ == "__main__":
    main()
