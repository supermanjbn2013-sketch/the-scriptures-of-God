#!/usr/bin/env python3
"""Import the Greek Epistle of Barnabas from pinned Perseus/First1KGreek TEI.

Text follows Kirsopp Lake's 1912 printed edition. It is not a diplomatic
transcription of one ancient codex. Section labels, printed page markers,
editorial notes and cross-references are preserved separately.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/barnabas")
REV = "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
SOURCE_PATH = "data/tlg1216/tlg001/tlg1216.tlg001.opp-grc1.xml"
SOURCE_URL = f"https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/{REV}/{SOURCE_PATH}"
REPO_URL = f"https://github.com/OpenGreekAndLatin/First1KGreek/tree/{REV}/data/tlg1216/tlg001"
LICENSE = "CC BY-SA 4.0"
EDITION = "Kirsopp Lake, The Apostolic Fathers, volume 1 (1912), Epistle of Barnabas"
ATTRIBUTION = "Epistle of Barnabas, Greek text edited by Kirsopp Lake, The Apostolic Fathers, volume 1 (1912); digitized and encoded by the Perseus Digital Library / Open Greek and Latin First1KGreek, CC BY-SA 4.0."


def local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def norm(value):
    return re.sub(r"\\s+", " ", value or "").strip()


def section_content(section):
    pages, notes, refs, pieces = [], [], [], []

    def walk(node, inside_note=False):
        tag = local(node.tag)
        if tag == "pb":
            page = node.attrib.get("n", "")
            if page and page not in pages:
                pages.append(page)
            return
        if tag == "note":
            value = norm("".join(node.itertext()))
            if value:
                notes.append({"text": value, "number": node.attrib.get("n", "")})
            for child in node.iter():
                if local(child.tag) == "bibl":
                    refs.append({"text": norm("".join(child.itertext()))})
            return
        if tag == "bibl":
            value = norm("".join(node.itertext()))
            if value:
                refs.append({"text": value})
            return
        if node.text:
            pieces.append(node.text)
        for child in list(node):
            walk(child)
            if child.tail:
                pieces.append(child.tail)

    for child in list(section):
        walk(child)
    return norm("".join(pieces)), pages, notes, refs


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    source = ROOT / "barnabas_source.xml"
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, source.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    root = ET.parse(source).getroot()
    edition = next((e for e in root.iter() if local(e.tag) == "div" and e.attrib.get("type") == "edition"), None)
    if edition is None:
        raise SystemExit("Barnabas Greek edition division missing from source TEI.")

    chapters, records = [], []
    chapter_divs = [e for e in list(edition) if local(e.tag) == "div" and e.attrib.get("subtype") == "chapter"]
    for chapter_div in chapter_divs:
        chapter = chapter_div.attrib.get("n", "")
        if not chapter:
            continue
        section_count = 0
        for section in list(chapter_div):
            if local(section.tag) != "div" or section.attrib.get("subtype") != "section":
                continue
            section_no = section.attrib.get("n", "")
            if not section_no:
                continue
            text, pages, notes, refs = section_content(section)
            if not text:
                continue
            records.append({
                "work": "Epistle of Barnabas",
                "chapter": chapter,
                "section": section_no,
                "reference": f"Barnabas {chapter}:{section_no}",
                "language": "grc",
                "text": text,
                "source_pages": pages,
                "editorial_notes": notes,
                "cross_references": refs,
                "edition": EDITION,
                "source_revision": REV,
                "source_url": SOURCE_URL,
                "license": LICENSE,
                "attribution": ATTRIBUTION,
                "textual_basis": "Kirsopp Lake's 1912 printed Greek edition; not a direct diplomatic transcription of one ancient manuscript."
            })
            section_count += 1
        if section_count == 0:
            raise SystemExit(f"Barnabas chapter {chapter} contains no imported sections.")
        chapters.append({"chapter": chapter, "section_count": section_count})

    if len(chapters) != 21 or len(records) != 194:
        raise SystemExit(f"Barnabas import rejected: {len(chapters)} chapters, {len(records)} sections; expected 21 and 194.")

    with (ROOT / "barnabas_greek.jsonl").open("w", encoding="utf-8", newline="\\n") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\\n")

    index = {
        "schema_version": 1,
        "work": "Epistle of Barnabas",
        "language": "Ancient Greek",
        "language_code": "grc",
        "chapter_count": len(chapters),
        "section_count": len(records),
        "chapters": chapters,
        "edition": EDITION,
        "textual_basis": "Lake's 1912 printed Greek edition; not a diplomatic transcription of one ancient manuscript.",
        "source_revision": REV,
        "source_url": SOURCE_URL,
        "repository_url": REPO_URL,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "limitations": [
            "The imported text follows the printed Greek edition of Kirsopp Lake (1912), not a direct diplomatic transcription of one ancient manuscript.",
            "Printed page markers, chapter and section divisions, editorial notes and cross-references are retained.",
            "Editorial notes and cross-references are stored separately from the Greek body text.",
            "The digital TEI transcription is CC BY-SA 4.0; attribution and share-alike terms must be preserved.",
            "No missing wording is reconstructed."
        ],
        "asset_file": "other_reference/barnabas/barnabas_greek.jsonl"
    }
    (ROOT / "barnabas_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(ATTRIBUTION + "\\nLicense: " + LICENSE + "\\nSource: " + SOURCE_URL + "\\n", encoding="utf-8")
    print(f"Imported Epistle of Barnabas: {len(chapters)} chapters, {len(records)} Greek sections.")


if __name__ == "__main__":
    main()
