#!/usr/bin/env python3
"""Import the EOTC printed-edition Ge'ez text of 1 Enoch from Beta maṣāḥǝft.

Only the EOTCed edition division is used. The separate Dillmann/Jerabek edition
has a distinct non-commercial permission notice and is deliberately excluded.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/enoch_geez")
REV = "ff9d4981eba2084c4914ca840ff323d85cbd2a1d"
PATH = "1001-2000/LIT1340EnochE.xml"
URL = f"https://raw.githubusercontent.com/BetaMasaheft/Works/{REV}/{PATH}"
LICENSE = "CC BY-SA 4.0"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
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
    request = urllib.request.Request(URL, headers={"User-Agent":"The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    source_path = ROOT / "LIT1340EnochE.xml"
    source_path.write_bytes(data)
    root = ET.fromstring(data)
    edition = next((node for node in root.iter()
                    if local(node.tag) == "div"
                    and node.attrib.get("type") == "edition"
                    and node.attrib.get(XML_LANG) == "gez"
                    and node.attrib.get(XML_ID) == "EOTCed"), None)
    if edition is None:
        raise SystemExit("The pinned TEI file has no EOTCed Ge'ez edition section.")

    records = []
    chapters = set()
    for part in edition.iter():
        if local(part.tag) != "div" or part.attrib.get("type") != "textpart" or part.attrib.get("subtype") != "chapter":
            continue
        match = re.search(r"\d+", part.attrib.get("n", "") or part.attrib.get(XML_ID, ""))
        if not match:
            continue
        chapter = int(match.group(0))
        chapters.add(chapter)
        for ab in list(part):
            if local(ab.tag) != "ab":
                continue
            for line in list(ab):
                if local(line.tag) != "l":
                    continue
                verse = line.attrib.get("n", "").strip()
                value = flatten(line)
                if value:
                    records.append({
                        "work":"1 Enoch",
                        "edition":"eotc_printed",
                        "edition_title":"Ethiopian Orthodox Tewahedo Church printed edition",
                        "language":"gez",
                        "chapter":chapter,
                        "verse":verse,
                        "reference":f"1 Enoch {chapter}:{verse}" if verse else f"1 Enoch {chapter}",
                        "text":value,
                        "edition_basis":"EOTC printed Ge'ez edition encoded in Beta maṣāḥǝft TEI; EOTCed division only",
                        "source_revision":REV,
                        "source_url":URL,
                        "license":LICENSE,
                        "attribution":"Beta maṣāḥǝft, Hiob-Ludolf Centre for Ethiopian Studies, Universität Hamburg; Ethiopian Orthodox Tewahedo Church printed edition."
                    })
    if len(chapters) != 108 or len(records) < 800:
        raise SystemExit(f"Unexpected EOTC Ge'ez coverage: {len(chapters)} chapters, {len(records)} verse records.")
    with (ROOT/"enoch_geez.jsonl").open("w",encoding="utf-8",newline="\n") as out:
        for record in records:
            out.write(json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n")
    index = {
        "schema_version":1,
        "work":"1 Enoch",
        "language":"Classical Ethiopic (Ge'ez)",
        "language_code":"gez",
        "source_repository":"Beta maṣāḥǝft / Works",
        "source_revision":REV,
        "source_url":URL,
        "license":LICENSE,
        "edition":"Ethiopian Orthodox Tewahedo Church printed edition (EOTCed)",
        "chapters":sorted(chapters),
        "chapter_count":len(chapters),
        "record_count":len(records),
        "textual_basis":"Complete Ge'ez edition division, kept separate from the Qumran Aramaic fragments and the edited Greek fragments.",
        "limitations":[
            "This is an edition-based Ge'ez text, not a fresh diplomatic transcription of one named ancient codex.",
            "The separate Dillmann/Jerabek edition division is excluded because it carries a distinct non-commercial permission notice.",
            "Ge'ez is a versional witness and does not supply Hebrew or Aramaic wording.",
            "Qumran Aramaic fragments and Greek fragments remain separately identified; no languages are silently merged."
        ],
        "asset_file":"other_reference/enoch_geez/enoch_geez.jsonl",
        "attribution":"Beta maṣāḥǝft, Hiob-Ludolf Centre for Ethiopian Studies, Universität Hamburg; EOTC printed edition; CC BY-SA 4.0."
    }
    (ROOT/"enoch_geez_index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"SOURCE_NOTICE.txt").write_text("Beta maṣāḥǝft, LIT1340EnochE.xml, pinned revision "+REV+"\nEdition division: EOTCed only (EOTC printed Ge'ez edition)\nLicense: CC BY-SA 4.0\nThe separate Dillmann/Jerabek division is excluded because it has a distinct non-commercial permission notice.\n",encoding="utf-8")
    print(f"Imported 1 Enoch Ge'ez EOTC edition: {len(chapters)} chapters, {len(records)} verse records (CC BY-SA 4.0).")

if __name__ == "__main__":
    main()
