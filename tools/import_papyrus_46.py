#!/usr/bin/env python3
"""Import the published Papyrus 46 (GA 03) TEI transcription for offline reading.

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

ROOT = pathlib.Path("app/src/main/assets/papyri/p46")
PAGES = ROOT / "pages"
SOURCE_URL = "https://ntvmr.uni-muenster.de/community/api/transcript/get/?docID=10046&pageID=ALL&format=teiraw"
ATTRIBUTION = "Papyrus 46 (GA P46), New Testament transcription by the Institut für Neutestamentliche Textforschung, New Testament Virtual Manuscript Room."
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
        raise ValueError("Unsafe or missing P46 page identifier: " + repr(value))
    return value + ".jsonl.gz"


def visible_text(elem):
    def collect(node):
        tag = lname(node.tag)
        if tag == "note":
            return ""
        inner = (node.text or "") + "".join(collect(child) + (child.tail or "") for child in list(node))
        return "[" + inner + "]" if tag == "supplied" and inner else inner
    return collect(elem)


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
            chosen = first if first is not None else (corrections[0] if corrections else None)
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
    xml_path = pathlib.Path(tempfile.gettempdir()) / "ntvmr_p46.xml"
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
                pages[page_id] = {"page_id": page_id, "asset_file": "papyri/p46/pages/" + filename, "record_count": 0}
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
                    label = elem.attrib.get("n", "")
                    if "inscriptio" in label.lower() or "subscriptio" in label.lower():
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
        raise SystemExit(f"Import rejected: unexpectedly small Papyrus 46 transcription ({len(pages)} pages, {total_records} records, {total_with_text} with text).")

    index = {
        "schema_version": 1,
        "record_type": "papyrus_46_page_verse_transcription",
        "manuscript": "Papyrus 46 (GA P46; Chester Beatty Biblical Papyrus II / P.Mich. inv. 6238)",
        "language": "Koine Greek",
        "document_id": 10046,
        "source_url": SOURCE_URL,
        "provider": "Institut für Neutestamentliche Textforschung, New Testament Virtual Manuscript Room",
        "attribution": ATTRIBUTION,
        "license": LICENSE,
        "license_url": LICENSE_URL,
        "record_count": total_records,
        "text_record_count": total_with_text,
        "page_count": len(pages),
        "pages": sorted(pages.values(), key=lambda item: item["page_id"]),
        "scope_note": "Surviving pages of P46 only. The codex originally comprised approximately 104 leaves, of which 86 survive; the opening and ending are lost. The transcription records only the surviving witness and retains source omissions and correction notes. Editorial restorations are bracketed where encoded by the source.",
        "text_handling": "Source labels and page/column/line coordinates are retained where present. Supplied readings are bracketed when encoded by the source. Missing manuscript portions are not supplied."
    }
    (ROOT / "p46_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(
        ATTRIBUTION + "\nLicense: " + LICENSE + "\nSource: " + SOURCE_URL + "\n"
        "Source labels and page/column/line coordinates are retained where available.\n"
        "Supplied readings are bracketed where encoded by the source. Missing manuscript portions are not supplied.\n",
        encoding="utf-8"
    )
    print(f"Imported Papyrus 46: {len(pages)} pages, {total_records} page-linked records, {total_with_text} records with text.")


if __name__ == "__main__":
    main()
