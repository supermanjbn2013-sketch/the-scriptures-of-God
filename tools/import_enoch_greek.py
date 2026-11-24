#!/usr/bin/env python3
"""Import the Greek fragment text of 1 Enoch from the pinned First1KGreek TEI edition.

Only Greek-language paragraphs inside the edition's Greek text section are
included. German translation, introduction, commentary and apparatus are not
silently mixed into the Greek dataset. Source page and chapter/section labels
are retained. This is an edited printed text, not a diplomatic transcription
of one ancient manuscript.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/enoch_greek")
REV = "a1e7714108a71af5124e934038d06ba30003dc0c"
SOURCE_PATH = "volume_xml/henoch.1901.xml"
SOURCE_URL = f"https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/{REV}/{SOURCE_PATH}"
REPO_URL = f"https://github.com/OpenGreekAndLatin/First1KGreek/tree/{REV}/{SOURCE_PATH}"
LICENSE = "CC BY-SA 4.0"
ATTRIBUTION = ("Johannes Flemming, ed., Das Buch Henoch (Leipzig: J. C. Hinrichs, 1901); "
               "digital TEI transcription by Open Greek and Latin, First1KGreek, "
               "CC BY-SA 4.0.")
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
GREEK = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")
ALPHA = re.compile(r"[^\W\d_]", re.UNICODE)


def local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def flatten(node):
    parts = []
    if node.text:
        parts.append(node.text)
    for child in list(node):
        tag = local(child.tag)
        if tag == "lb":
            number = child.attrib.get("n", "")
            parts.append(f" [line {number}] " if number else " ")
        elif tag == "gap":
            parts.append(" [lacuna] ")
        else:
            parts.append(flatten(child))
        if child.tail:
            parts.append(child.tail)
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def greek_ratio(value):
    letters = ALPHA.findall(value)
    if not letters:
        return 0.0
    return sum(1 for ch in letters if GREEK.match(ch)) / len(letters)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    source = ROOT / "henoch_1901_source.xml"
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, source.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    root = ET.parse(source).getroot()
    edition = next((node for node in root.iter() if local(node.tag) == "div"
                    and node.attrib.get("type") == "edition"
                    and node.attrib.get("subtype") == "work"), None)
    if edition is None:
        raise SystemExit("Pinned Henoch TEI has no Greek edition section.")

    records = []
    state = {"page": "", "chapter": "", "section": ""}

    def walk(node):
        tag = local(node.tag)
        if tag == "pb":
            state["page"] = node.attrib.get("n", "")
            return
        if tag == "div" and node.attrib.get("type") == "textpart":
            subtype = node.attrib.get("subtype", "")
            if subtype == "chapter":
                state["chapter"] = node.attrib.get("n", "")
                state["section"] = ""
            elif subtype == "section":
                state["section"] = node.attrib.get("n", "")
        if tag == "p":
            text = flatten(node)
            if greek_ratio(text) >= 0.45:
                records.append({
                    "work": "1 Enoch",
                    "language": "grc",
                    "text": text,
                    "reference": "1 Enoch " + (state["chapter"] or "?") + ":" + (state["section"] or "?"),
                    "chapter": state["chapter"],
                    "section": state["section"],
                    "printed_page": state["page"],
                    "edition": "Johannes Flemming, Das Buch Henoch (1901), Greek text",
                    "editorial_basis": "Edited Greek text in a printed critical edition; not a diplomatic transcription of one ancient codex.",
                    "source_revision": REV,
                    "source_url": SOURCE_URL,
                    "repository_url": REPO_URL,
                    "license": LICENSE,
                    "attribution": ATTRIBUTION
                })
            return
        for child in list(node):
            walk(child)

    walk(edition)
    if len(records) < 15:
        raise SystemExit(f"Greek Enoch import rejected: only {len(records)} Greek paragraphs found.")

    pages = sorted({int(r["printed_page"]) for r in records if r["printed_page"].isdigit()})
    chapters = sorted({int(r["chapter"]) for r in records if r["chapter"].isdigit()})
    sections = sorted({(int(r["chapter"]), int(r["section"])) for r in records
                       if r["chapter"].isdigit() and r["section"].isdigit()})

    with (ROOT / "enoch_greek.jsonl").open("w", encoding="utf-8", newline="\n") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    index = {
        "schema_version": 1,
        "work": "1 Enoch",
        "language": "Ancient Greek",
        "edition": "Johannes Flemming, ed., Das Buch Henoch (Leipzig: J. C. Hinrichs, 1901)",
        "textual_scope": "Greek fragment text and Greek portions preserved in the 1901 edition; not a complete Greek copy of 1 Enoch.",
        "record_count": len(records),
        "printed_pages": pages,
        "chapter_count": len(chapters),
        "chapters": chapters,
        "section_count": len(sections),
        "source_revision": REV,
        "source_url": SOURCE_URL,
        "repository_url": REPO_URL,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "status": "Imported offline as edition-derived Greek text paragraphs, with printed page and section references.",
        "limitations": [
            "The Greek text is fragmentary; it is not a complete Greek manuscript of 1 Enoch.",
            "This is an edited printed Greek text, not a diplomatic transcription of one ancient codex.",
            "The source edition includes editorial readings and a critical apparatus; paragraph text is retained separately from apparatus notes.",
            "The German translation, introduction and commentary are not included in this Greek dataset.",
            "The Aramaic Qumran witnesses and Ethiopic manuscript tradition remain separate datasets.",
            "No missing wording is reconstructed by this app."
        ],
        "asset_file": "other_reference/enoch_greek/enoch_greek.jsonl"
    }
    (ROOT / "enoch_greek_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(ATTRIBUTION + "\nLicense: " + LICENSE + "\nSource: " + SOURCE_URL + "\n", encoding="utf-8")
    print(f"Imported 1 Enoch Greek edition text: {len(records)} paragraphs, {len(pages)} printed pages, {len(sections)} chapter/section references (CC BY-SA 4.0).")


if __name__ == "__main__":
    main()
