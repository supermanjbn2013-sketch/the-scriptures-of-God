#!/usr/bin/env python3
"""Import the Greek Shepherd of Hermas from the pinned First1KGreek TEI edition.

This is Kirsopp Lake's 1917 printed Greek edition, not a direct diplomatic
transcription of any one manuscript. Book/chapter/section identifiers, source
page markers, editorial notes and cross-references are retained.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/hermas")
REV = "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
SOURCE_PATH = "data/tlg1419/tlg001/tlg1419.tlg001.1st1K-grc1.xml"
SOURCE_URL = f"https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/{REV}/{SOURCE_PATH}"
REPO_URL = f"https://github.com/OpenGreekAndLatin/First1KGreek/tree/{REV}/{SOURCE_PATH}"
LICENSE = "CC BY-SA 4.0"
ATTRIBUTION = "Hermas, The Shepherd, Greek text edited by Kirsopp Lake, The Apostolic Fathers, volume 2 (1917); digital TEI transcription by Open Greek and Latin / First1KGreek, CC BY-SA 4.0."


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def clean_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    source = ROOT / "hermas_source.xml"
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
        raise SystemExit("Shepherd of Hermas edition division is missing from source TEI.")

    records = []
    books = []
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
                        refs.append({"text": clean_space("".join(bibl.itertext())), "corresp": bibl.attrib.get("corresp", "")})
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

    for book_div in list(edition):
        if lname(book_div.tag) != "div" or book_div.attrib.get("subtype") != "book":
            continue
        book = book_div.attrib.get("n", "")
        if not book:
            continue
        head = next((x for x in list(book_div) if lname(x.tag) == "head"), None)
        title = clean_space("".join(head.itertext())) if head is not None else ""
        if "Ὅρασις" in title:
            part_type = "Vision"
        elif "Ἐντολή" in title:
            part_type = "Mandate"
        elif "Παραβολή" in title:
            part_type = "Similitude"
        else:
            part_type = "Book"
        count = 0
        for chapter_div in list(book_div):
            if lname(chapter_div.tag) != "div" or chapter_div.attrib.get("subtype") != "chapter":
                continue
            chapter = chapter_div.attrib.get("n", "")
            for section_div in list(chapter_div):
                if lname(section_div.tag) != "div" or section_div.attrib.get("subtype") != "section":
                    continue
                section = section_div.attrib.get("n", "")
                if not chapter or not section:
                    continue
                text, pages, refs, notes = extract(section_div)
                if not text:
                    continue
                records.append({
                    "work": "Shepherd of Hermas",
                    "book": int(book),
                    "book_title": title,
                    "part_type": part_type,
                    "chapter": int(chapter),
                    "section": int(section),
                    "reference": f"Hermas {part_type} {book}:{chapter}:{section}",
                    "language": "grc",
                    "text": text,
                    "source_pages": pages,
                    "cross_references": refs,
                    "editorial_notes": notes,
                    "edition": "Kirsopp Lake, The Apostolic Fathers, volume 2 (1917)",
                    "source_revision": REV,
                    "source_url": SOURCE_URL,
                    "license": LICENSE,
                    "attribution": ATTRIBUTION,
                    "textual_basis": "Printed Greek edition derived from manuscript transmission; not a direct diplomatic manuscript transcription."
                })
                count += 1
        books.append({"book": int(book), "book_title": title, "part_type": part_type, "section_count": count})

    if len(books) != 27 or len(records) < 500 or any(x["section_count"] == 0 for x in books):
        raise SystemExit(f"Shepherd of Hermas import rejected: {len(books)} divisions, {len(records)} sections.")

    with (ROOT / "hermas_greek.jsonl").open("w", encoding="utf-8", newline="\n") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    index = {
        "schema_version": 1,
        "work": "Shepherd of Hermas",
        "language": "Ancient Greek",
        "book_count": len(books),
        "section_count": len(records),
        "books": books,
        "edition": "Kirsopp Lake, The Apostolic Fathers, volume 2 (1917)",
        "textual_basis": "Printed Greek edition derived from the manuscript tradition; not a direct diplomatic transcription of a single manuscript.",
        "witness_note": "The work survives in multiple Greek manuscripts and ancient translations; this digital text follows Lake's 1917 printed edition.",
        "source_revision": REV,
        "source_url": SOURCE_URL,
        "repository_url": REPO_URL,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "limitations": [
            "This is a printed-edition-derived Greek text, not a direct diplomatic transcription of one manuscript.",
            "The Greek manuscript tradition and ancient translations contain textual variation.",
            "Book, chapter and section numbering, source page markers, editorial notes and cross-references are retained.",
            "The digital transcription and encoding are distributed under CC BY-SA 4.0.",
            "No missing wording is reconstructed."
        ],
        "asset_file": "other_reference/hermas/hermas_greek.jsonl"
    }
    (ROOT / "hermas_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(ATTRIBUTION + "\nLicense: " + LICENSE + "\nSource: " + SOURCE_URL + "\n", encoding="utf-8")
    print(f"Imported Shepherd of Hermas Greek text: {len(books)} divisions, {len(records)} sections (CC BY-SA 4.0).")


if __name__ == "__main__":
    main()
