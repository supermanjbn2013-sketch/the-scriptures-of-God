#!/usr/bin/env python3
"""Import the published Codex Vaticanus (GA 03) TEI transcription for offline reading.

Source: Institut für Neutestamentliche Textforschung, NTVMR, document 20003.
The importer preserves the source verse labels and page/column/line identifiers.
For corrected readings, the original hand is displayed and correction readings
are retained as notes. Missing manuscript portions are never supplied.
"""
import gzip
import json
import pathlib
import re
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/vaticanus")
PAGES = ROOT / "pages"
SOURCE_URL = "https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/?docID=20003&pageID=ALL&format=teiraw"
ATTRIBUTION = "Codex Vaticanus (GA 03), New Testament transcription by the Institut für Neutestamentliche Textforschung, New Testament Virtual Manuscript Room."
LICENSE = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
USER_AGENT = "The-Scriptures-of-God-Archive/1.0"
OMITTED = "OM"


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def marker_id(elem):
    return elem.attrib.get(XML_ID) or elem.attrib.get("id") or elem.attrib.get("n") or elem.attrib.get("folionum") or ""


def safe_file(value):
    if not value or not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        raise ValueError("Unsafe or missing Vaticanus page identifier: " + repr(value))
    return value + ".jsonl.gz"


def visible_text(elem):
    parts = []
    for node in elem.iter():
        if lname(node.tag) == "note":
            continue
        if node.text:
            parts.append(node.text)
        if node.tail and lname(node.tag) not in ("note",):
            parts.append(node.tail)
    return "".join(parts)


def extract_block(block):
    words = []
    notes = []
    coordinates = {"page_ids": [], "column_ids": [], "line_ids": []}

    def add_marker(kind, elem):
        value = marker_id(elem)
        if value and value not in coordinates[kind]:
            coordinates[kind].append(value)

    def walk(elem):
        tag = lname(elem.tag)
        if tag == "note":
            return
        if tag == "pb":
            add_marker("page_ids", elem)
            return
        if tag == "cb":
            add_marker("column_ids", elem)
            return
        if tag == "lb":
            add_marker("line_ids", elem)
            return
        if tag == "app":
            readings = [child for child in list(elem) if lname(child.tag) == "rdg"]
            first = next((r for r in readings if r.attrib.get("type") == "orig"), None)
            corrections = [r for r in readings if r.attrib.get("type") == "corr"]
            chosen = first or (corrections[0] if corrections else None)
            if chosen is not None:
                if first is not None and corrections:
                    before = " ".join((visible_text(first) or "").split())
                    correction_texts = []
                    for correction in corrections:
                        after = " ".join((visible_text(correction) or "").split()) or "om."
                        hand = correction.attrib.get("hand", "corr.")
                        correction_texts.append(after + " (" + hand + ")")
                    notes.append("First hand: " + (before or "—") + "; corrections: " + "; ".join(correction_texts))
                walk(chosen)
            return
        if tag == "w":
            value = " ".join((visible_text(elem) or "").split())
            if value and value != OMITTED:
                words.append(value)
            return
        if tag == "pc":
            value = " ".join((visible_text(elem) or "").split())
            if value:
                words.append(value)
            return
        for child in list(elem):
            walk(child)

    for child in list(block):
        walk(child)

    label = block.attrib.get("n") or block.attrib.get("id") or ""
    return {
        "source_label": label,
        "text": " ".join(words).strip(),
        "page_ids": coordinates["page_ids"],
        "column_ids": coordinates["column_ids"],
        "line_ids": coordinates["line_ids"],
        "correction_notes": notes
    }


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    xml_path = pathlib.Path(tempfile.gettempdir()) / "ntvmr_vaticanus_03.xml"
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response, xml_path.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    pages = {}
    total_records = 0
    total_with_text = 0
    current_page = ""
    current_column = ""
    current_line = ""
    handles = {}

    def write_record(record, inherited):
        nonlocal total_records, total_with_text
        page_ids = record["page_ids"] or ([inherited["page"]] if inherited["page"] else [])
        column_ids = record["column_ids"] or ([inherited["column"]] if inherited["column"] else [])
        line_ids = record["line_ids"] or ([inherited["line"]] if inherited["line"] else [])
        if not page_ids:
            return
        # A verse may cross a page break; retain it in each source page index, with its full coordinate list.
        for page_id in page_ids:
            filename = safe_file(page_id)
            if page_id not in handles:
                handle = gzip.open(PAGES / filename, "wt", encoding="utf-8", newline="\n", compresslevel=9)
                handles[page_id] = handle
                pages[page_id] = {"page_id": page_id, "asset_file": "vaticanus/pages/" + filename, "record_count": 0}
            payload = {
                "page_id": page_id,
                "column_ids": column_ids,
                "line_ids": line_ids,
                "source_label": record["source_label"],
                "text": record["text"],
                "correction_notes": record["correction_notes"]
            }
            handles[page_id].write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
            pages[page_id]["record_count"] += 1
            total_records += 1
            if record["text"]:
                total_with_text += 1

    try:
        with xml_path.open("rb") as source:
            stack = []
            for event, elem in ET.iterparse(source, events=("start", "end")):
                tag = lname(elem.tag)
                if event == "start":
                    if tag == "pb":
                        current_page = marker_id(elem)
                    elif tag == "cb":
                        current_column = marker_id(elem)
                    elif tag == "lb":
                        current_line = marker_id(elem)
                    if tag == "ab":
                        stack.append((elem, {"page": current_page, "column": current_column, "line": current_line}))
                    continue
                if tag == "ab" and stack and stack[-1][0] is elem:
                    _, inherited = stack.pop()
                    parent_type = ""
                    parent = elem.getparent() if hasattr(elem, "getparent") else None
                    if parent is not None:
                        parent_type = parent.attrib.get("type", "").lower()
                    label = elem.attrib.get("n", "")
                    if parent_type in ("incipit", "explicit") or "inscriptio" in label.lower() or "subscriptio" in label.lower():
                        elem.clear()
                        continue
                    record = extract_block(elem)
                    if record["text"]:
                        write_record(record, inherited)
                    elem.clear()
    finally:
        for handle in handles.values():
            handle.close()

    if not pages or total_records < 1000 or total_with_text < 1000:
        raise SystemExit(f"Import rejected: unexpectedly small Vaticanus transcription ({len(pages)} pages, {total_records} records, {total_with_text} with text).")

    index = {
        "schema_version": 1,
        "record_type": "codex_vaticanus_page_verse_transcription",
        "manuscript": "Codex Vaticanus (GA 03; Vat.gr.1209)",
        "language": "Koine Greek",
        "document_id": 20003,
        "source_url": SOURCE_URL,
        "provider": "Institut für Neutestamentliche Textforschung, New Testament Virtual Manuscript Room",
        "attribution": ATTRIBUTION,
        "license": LICENSE,
        "license_url": LICENSE_URL,
        "record_count": total_records,
        "text_record_count": total_with_text,
        "page_count": len(pages),
        "pages": sorted(pages.values(), key=lambda item: item["page_id"]),
        "scope_note": "Original surviving New Testament transcription only. The original codex does not preserve the Pastoral Letters, Philemon, Revelation, or Hebrews after 9:14. The later Revelation supplement is excluded.",
        "text_handling": "The original hand is displayed where the source distinguishes corrections; correction readings are retained as notes. Source labels and page/column/line coordinates are retained where present. Missing manuscript portions are not supplied."
    }
    (ROOT / "vaticanus_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(
        ATTRIBUTION + "\nLicense: " + LICENSE + "\nSource: " + SOURCE_URL + "\n"
        "Original-hand readings are displayed where marked by the source; corrections are notes.\n"
        "Original source labels and page/column/line coordinates are retained where available.\n"
        "Missing manuscript portions are not supplied. The later Revelation supplement is excluded.\n",
        encoding="utf-8"
    )
    print(f"Imported Codex Vaticanus: {len(pages)} pages, {total_records} page-linked records, {total_with_text} records with text.")


if __name__ == "__main__":
    main()
