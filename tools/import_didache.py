#!/usr/bin/env python3
"""Import the Greek Didache text from the pinned First1KGreek TEI edition.

This is a printed-edition-derived Greek text (Kirsopp Lake, 1912), not a
direct diplomatic transcription of the sole complete manuscript. The source
TEI's chapter/section numbers, page markers, notes and cross-references are
retained. No missing wording is reconstructed.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/didache")
REV = "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
SOURCE_PATH = "data/tlg1311/tlg001/tlg1311.tlg001.1st1K-grc1.xml"
SOURCE_URL = f"https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/{REV}/{SOURCE_PATH}"
REPO_URL = f"https://github.com/OpenGreekAndLatin/First1KGreek/tree/{REV}/{SOURCE_PATH}"
LICENSE = "CC BY-SA 4.0"
ATTRIBUTION = "Kirsopp Lake, The Apostolic Fathers, volume 1 (1912), Didache Greek text; digital TEI transcription by Open Greek and Latin / First1KGreek, CC BY-SA 4.0."
NS = "{http://www.tei-c.org/ns/1.0}"


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def clean_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    source = ROOT / "didache_source.xml"
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, source.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    tree = ET.parse(source)
    root = tree.getroot()
    edition = next((e for e in root.iter() if lname(e.tag) == "div" and e.attrib.get("type") == "edition"), None)
    if edition is None:
        raise SystemExit("Didache edition division is missing from the source TEI.")

    records = []
    chapter_counts = {}
    title = ""
    for child in list(edition):
        if lname(child.tag) == "head":
            title = clean_space("".join(child.itertext()))
            break

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

    for chapter_div in list(edition):
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
                "work": "Didache",
                "chapter": int(chapter),
                "section": int(section),
                "reference": f"Didache {chapter}:{section}",
                "language": "grc",
                "text": text,
                "source_pages": pages,
                "cross_references": refs,
                "editorial_notes": notes,
                "edition": "Kirsopp Lake, The Apostolic Fathers, vol. 1 (1912)",
                "source_revision": REV,
                "source_url": SOURCE_URL,
                "license": LICENSE,
                "attribution": ATTRIBUTION,
                "textual_basis": "Printed Greek edition derived from manuscript transmission; not a direct diplomatic manuscript transcription."
            })
            chapter_counts[chapter] += 1

    if len(records) < 90 or len(chapter_counts) != 16 or any(n == 0 for n in chapter_counts.values()):
        raise SystemExit(f"Didache import rejected: {len(records)} sections across {len(chapter_counts)} chapters.")

    with (ROOT / "didache_greek.jsonl").open("w", encoding="utf-8", newline="\n") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    index = {
        "schema_version": 1,
        "work": "Didache (Teaching of the Twelve Apostles)",
        "language": "Ancient Greek",
        "title_in_source": title,
        "chapter_count": len(chapter_counts),
        "section_count": len(records),
        "chapters": [{"chapter": int(k), "section_count": v} for k, v in sorted(chapter_counts.items(), key=lambda x: int(x[0]))],
        "edition": "Kirsopp Lake, The Apostolic Fathers, volume 1 (1912)",
        "textual_basis": "Printed Greek edition derived from the manuscript tradition; not a direct diplomatic transcription of Codex Hierosolymitanus 54.",
        "primary_complete_witness": "Codex Hierosolymitanus 54, copied in 1056; the source edition is not a page-by-page manuscript transcription.",
        "source_revision": REV,
        "source_url": SOURCE_URL,
        "repository_url": REPO_URL,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "limitations": [
            "The surviving complete Greek manuscript is Codex Hierosolymitanus 54 (1056); this import is Lake's 1912 printed Greek edition.",
            "The Greek text is not represented as a direct transcription of the manuscript pages.",
            "Source chapter and section numbering, printed-edition page markers, cross-references and editorial notes are retained.",
            "The digital transcription and encoding are distributed under CC BY-SA 4.0.",
            "No missing wording is reconstructed."
        ],
        "asset_file": "other_reference/didache/didache_greek.jsonl"
    }
    (ROOT / "didache_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(ATTRIBUTION + "\nLicense: " + LICENSE + "\nSource: " + SOURCE_URL + "\n", encoding="utf-8")
    print(f"Imported Didache Greek text: {len(chapter_counts)} chapters, {len(records)} sections (CC BY-SA 4.0).")


if __name__ == "__main__":
    main()
