#!/usr/bin/env python3
"""Import the Ge'ez edition text of Ascension of Isaiah from Beta maṣāḥǝft.

The TEI edition is based on the Library of Ethiopic Texts transcription of
R. H. Charles's edition. Its file declares CC BY-SA 4.0 for the encoding and
a separate non-commercial-only permission for the underlying Ge'ez text.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/ascension_isaiah")
REV = "671a29177071f19cc9da990aaad1681b338cdb49"
PATH = "1001-2000/LIT1671Isaiah.xml"
URL = f"https://raw.githubusercontent.com/BetaMasaheft/Works/{REV}/{PATH}"
LICENSE = "CC BY-SA 4.0 (TEI encoding); underlying Ge'ez text: non-commercial use only"
ATTRIBUTION = ("Michal Jerabek, Library of Ethiopic Texts (1995); Unicode conversion by Ran HaCohen; "
               "TEI encoding and curation by Beta maṣāḥǝft, Universität Hamburg. "
               "CC BY-SA 4.0 for the TEI file; underlying text permission is non-commercial only.")
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def flatten(node):
    parts = []
    if node.text:
        parts.append(node.text)
    for child in list(node):
        tag = local(child.tag)
        if tag in ("lb", "pb", "cb"):
            parts.append(" ")
        elif tag == "gap":
            parts.append(" [lacuna] ")
        elif tag == "supplied":
            parts.append("[" + flatten(child) + "]")
        else:
            parts.append(flatten(child))
        if child.tail:
            parts.append(child.tail)
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    source = ROOT / "LIT1671Isaiah.xml"
    request = urllib.request.Request(URL, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, source.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    root = ET.parse(source).getroot()
    editions = [node for node in root.iter() if local(node.tag) == "div"
                and node.attrib.get("type") == "edition"
                and node.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") == "gez"]
    if not editions:
        raise SystemExit("Beta maṣāḥǝft file has no Ge'ez edition division.")

    records = []
    for edition in editions:
        for section in edition.iter():
            if local(section.tag) != "div" or section.attrib.get("type") != "textpart":
                continue
            if section.attrib.get("subtype") != "section":
                continue
            number = section.attrib.get("n", "")
            for node in list(section):
                if local(node.tag) != "ab":
                    continue
                value = flatten(node)
                if value:
                    records.append({
                        "work": "Ascension of Isaiah",
                        "language": "gez",
                        "section": number,
                        "reference": f"Ascension of Isaiah, section {number}",
                        "text": value,
                        "edition_basis": "Library of Ethiopic Texts transcription (1995), encoded in TEI by Beta maṣāḥǝft",
                        "source_revision": REV,
                        "source_url": URL,
                        "license": LICENSE,
                        "attribution": ATTRIBUTION,
                        "reuse_restriction": "Non-commercial use only for the underlying Ge'ez text; no commercial redistribution."
                    })
    if len(records) < 10:
        raise SystemExit(f"Ascension of Isaiah import rejected: only {len(records)} Ge'ez sections found.")
    numbers = sorted({int(r["section"]) for r in records if r["section"].isdigit()})
    with (ROOT / "ascension_isaiah_geez.jsonl").open("w", encoding="utf-8", newline="\n") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    index = {
        "schema_version": 1,
        "work": "Ascension of Isaiah",
        "language": "Classical Ethiopic (Ge'ez)",
        "edition_basis": "Library of Ethiopic Texts transcription (1995), encoded in TEI by Beta maṣāḥǝft",
        "section_count": len(numbers),
        "record_count": len(records),
        "sections": numbers,
        "source_revision": REV,
        "source_url": URL,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "status": "Imported offline as Ge'ez edition text, separated by source section.",
        "limitations": [
            "This is an edition-based Unicode transcription, not a fresh diplomatic transcription of a single manuscript.",
            "The underlying text permission explicitly limits use to non-commercial purposes; it may not be sold or commercially redistributed.",
            "The Ge'ez text is the complete surviving language tradition, but it is a translation from a lost Greek textual form.",
            "Greek, Latin, Coptic and Slavonic witnesses are separate traditions and are not merged into this Ge'ez text.",
            "The source edition's manuscript basis and editorial decisions are not independently re-collated by this app.",
            "No missing wording is reconstructed."
        ],
        "asset_file": "other_reference/ascension_isaiah/ascension_isaiah_geez.jsonl"
    }
    (ROOT / "ascension_isaiah_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(ATTRIBUTION + "\nReuse restriction: non-commercial use only for the underlying Ge'ez text.\nSource: " + URL + "\n", encoding="utf-8")
    print(f"Imported Ascension of Isaiah Ge'ez text: {len(records)} text sections across {len(numbers)} numbered sections; non-commercial text restriction retained.")


if __name__ == "__main__":
    main()
