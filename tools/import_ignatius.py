#!/usr/bin/env python3
"""Import the seven Greek letters of Ignatius from pinned First1KGreek TEI.

The source is Kirsopp Lake's 1912 printed Greek edition, not a direct
transcription of one ancient manuscript. Chapter/section labels, page markers,
and editorial notes are retained. Notes are kept separate from the Greek body.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/ignatius")
REV = "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
SOURCE_PATH = "data/tlg1443/tlg001/tlg1443.tlg001.1st1K-grc1.xml"
SOURCE_URL = f"https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/{REV}/{SOURCE_PATH}"
REPO_URL = f"https://github.com/OpenGreekAndLatin/First1KGreek/tree/{REV}/{SOURCE_PATH}"
LICENSE = "CC BY-SA 4.0"
EDITION = "Kirsopp Lake, The Apostolic Fathers, volume 1 (1912)"
ATTRIBUTION = "Ignatius of Antioch, seven genuine letters, Greek text edited by Kirsopp Lake, The Apostolic Fathers, volume 1 (1912); digital TEI transcription by Perseus Digital Library / Open Greek and Latin First1KGreek, CC BY-SA 4.0."
NAMES = {
    "1": "To the Ephesians",
    "2": "To the Magnesians",
    "3": "To the Trallians",
    "4": "To the Romans",
    "5": "To the Philadelphians",
    "6": "To the Smyrnaeans",
    "7": "To Polycarp",
}


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def clean_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def extract(section):
    pages, refs, notes, chunks = [], [], [], []

    def walk(node):
        tag = lname(node.tag)
        if tag == "note":
            note_text = clean_space("".join(node.itertext()))
            if note_text:
                notes.append({"text": note_text, "number": node.attrib.get("n", "")})
            for bibl in node.iter():
                if lname(bibl.tag) == "bibl":
                    refs.append({
                        "text": clean_space("".join(bibl.itertext())),
                        "corresp": bibl.attrib.get("corresp", "")
                    })
            return
        if tag == "pb":
            page = node.attrib.get("n", "")
            if page and page not in pages:
                pages.append(page)
            return
        if node.text:
            chunks.append(node.text)
        for child in list(node):
            walk(child)
            if child.tail:
                chunks.append(child.tail)

    for node in list(section):
        walk(node)
    return clean_space("".join(chunks)), pages, refs, notes


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    source = ROOT / "ignatius_source.xml"
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, source.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    root = ET.parse(source).getroot()
    edition = next((e for e in root.iter() if lname(e.tag) == "div" and e.attrib.get("type") == "edition"), None)
    if edition is None:
        raise SystemExit("Ignatius Greek edition division is missing from source TEI.")

    records, letters = [], []
    for letter_div in list(edition):
        if lname(letter_div.tag) != "div" or letter_div.attrib.get("subtype") != "epistle":
            continue
        number = letter_div.attrib.get("n", "")
        if number not in NAMES:
            continue
        chapter_counts = {}
        for chapter_div in list(letter_div):
            if lname(chapter_div.tag) != "div" or chapter_div.attrib.get("subtype") != "chapter":
                continue
            chapter = chapter_div.attrib.get("n", "")
            if not chapter:
                continue
            chapter_counts[chapter] = 0
            for section_div in list(chapter_div):
                if lname(section_div.tag) != "div" or section_div.attrib.get("subtype") != "section":
                    continue
                section = section_div.attrib.get("n", "")
                if not section:
                    continue
                text, pages, refs, notes = extract(section_div)
                if not text:
                    continue
                records.append({
                    "work": "Letters of Ignatius",
                    "letter": number,
                    "letter_name": NAMES[number],
                    "chapter": chapter,
                    "section": section,
                    "reference": f"Ignatius, {NAMES[number]} {chapter}:{section}",
                    "language": "grc",
                    "text": text,
                    "source_pages": pages,
                    "cross_references": refs,
                    "editorial_notes": notes,
                    "edition": EDITION,
                    "source_revision": REV,
                    "source_url": SOURCE_URL,
                    "license": LICENSE,
                    "attribution": ATTRIBUTION,
                    "textual_basis": "Kirsopp Lake's printed Greek edition, derived from manuscript transmission; not a direct diplomatic transcription of a single manuscript."
                })
                chapter_counts[chapter] += 1
        if not chapter_counts or any(count == 0 for count in chapter_counts.values()):
            raise SystemExit(f"Ignatius letter {number} has missing chapter/section text.")
        letters.append({
            "number": number,
            "name": NAMES[number],
            "chapter_count": len(chapter_counts),
            "section_count": sum(chapter_counts.values()),
            "chapters": [{"chapter": key, "section_count": value} for key, value in chapter_counts.items()]
        })

    letters.sort(key=lambda item: int(item["number"]))
    if [item["number"] for item in letters] != list(NAMES) or len(records) < 150:
        raise SystemExit(f"Ignatius import rejected: {len(letters)} letters, {len(records)} sections.")
    with (ROOT / "ignatius_greek.jsonl").open("w", encoding="utf-8", newline="\\n") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\\n")

    index = {
        "schema_version": 1,
        "work": "Letters of Ignatius of Antioch (seven genuine letters)",
        "language": "Ancient Greek",
        "language_code": "grc",
        "letter_count": len(letters),
        "chapter_count": sum(item["chapter_count"] for item in letters),
        "section_count": len(records),
        "letters": letters,
        "edition": EDITION,
        "textual_basis": "Lake's 1912 printed Greek edition; not a diplomatic transcription of one ancient manuscript.",
        "source_revision": REV,
        "source_url": SOURCE_URL,
        "repository_url": REPO_URL,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "limitations": [
            "This source contains the seven letters treated as genuine in Lake's edition; it is not a complete catalogue of all writings attributed to Ignatius.",
            "The Greek text follows a printed edition and is not a direct diplomatic transcription of one ancient manuscript.",
            "Chapter and section labels, printed page markers, editorial notes and cross-references are retained.",
            "Editorial notes are stored separately from the Greek body text.",
            "The digital TEI transcription is CC BY-SA 4.0; preserve attribution and share-alike terms.",
            "No missing wording is reconstructed."
        ],
        "asset_file": "other_reference/ignatius/ignatius_greek.jsonl"
    }
    (ROOT / "ignatius_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(ATTRIBUTION + "\\nLicense: " + LICENSE + "\\nSource: " + SOURCE_URL + "\\n", encoding="utf-8")
    print(f"Imported Ignatius Greek text: {len(letters)} letters, {index['chapter_count']} chapter divisions, {len(records)} sections.")


if __name__ == "__main__":
    main()
