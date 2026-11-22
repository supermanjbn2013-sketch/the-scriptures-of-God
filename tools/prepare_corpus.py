#!/usr/bin/env python3
"""Build an attributed offline verse corpus from licensed upstream XML editions.
The script fails closed: a missing book, empty extraction, or malformed source stops the build.
"""
import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/corpus")
ROOT.mkdir(parents=True, exist_ok=True)
HEBREW = ["Gen","Exod","Lev","Num","Deut","Josh","Judg","Ruth","1Sam","2Sam","1Kgs","2Kgs","1Chr","2Chr","Ezra","Neh","Esth","Job","Ps","Prov","Eccl","Song","Isa","Jer","Lam","Ezek","Dan","Hos","Joel","Amos","Obad","Jonah","Mic","Nah","Hab","Zeph","Hag","Zech","Mal"]
GREEK = ["Matt","Mark","Luke","John","Acts","Rom","1Cor","2Cor","Gal","Eph","Phil","Col","1Thess","2Thess","1Tim","2Tim","Titus","Phlm","Heb","Jas","1Pet","2Pet","1John","2John","3John","Jude","Rev"]

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()

def local_name(tag):
    return tag.rsplit("}", 1)[-1].lower()

def clean(parts):
    return " ".join(" ".join(parts).split())

def extract_hebrew(book):
    url = f"https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/{book}.xml"
    root = ET.fromstring(fetch(url))
    out = []
    for verse in root.iter():
        if local_name(verse.tag) != "verse":
            continue
        ref = verse.attrib.get("osisID", "").strip()
        if not ref:
            continue
        # Preserve word order and the source's Hebrew characters. Do not normalize Unicode.
        tokens = []
        for node in verse.iter():
            if local_name(node.tag) == "w" and node.text:
                tokens.append(node.text)
        text = clean(tokens)
        if text:
            out.append({
                "ref": ref, "language": "he", "text": text,
                "source": "Open Scriptures Hebrew Bible (OSHB), based on the Westminster Leningrad Codex",
                "edition": "OSHB repository, wlc XML", "witness_basis": "Westminster Leningrad Codex",
                "transcription_type": "electronic edition text with OSHB annotations",
                "source_url": url, "text_status": "WLC base text is public domain; OSHB annotations CC BY 4.0",
                "attribution": "Open Scriptures Hebrew Bible Project: https://github.com/openscriptures/morphhb"
            })
    if not out:
        raise RuntimeError(f"No Hebrew verses extracted for {book} from {url}")
    return out

def extract_greek(book):
    url = f"https://raw.githubusercontent.com/Faithlife/SBLGNT/master/data/sblgnt/xml/{book}.xml"
    root = ET.fromstring(fetch(url))
    out = []
    current_ref = None
    parts = []
    def flush():
        if current_ref and parts:
            verse_text = clean(parts)
            if verse_text:
                out.append({
                    "ref": current_ref, "language": "grc", "text": verse_text,
                    "source": "SBL Greek New Testament v1.2",
                    "edition": "SBLGNT v1.2", "witness_basis": "Critically edited Greek text; not a single manuscript transcription",
                    "transcription_type": "edited Greek text",
                    "source_url": url, "license": "CC BY 4.0",
                    "attribution": "SBL Greek New Testament, © 2010 Society of Biblical Literature and Logos Bible Software. https://github.com/Faithlife/SBLGNT"
                })
    for node in root.iter():
        tag = local_name(node.tag)
        if tag == "verse-number":
            flush()
            current_ref = node.attrib.get("id", "").strip()
            parts = []
        elif current_ref and tag in ("w", "prefix", "suffix") and node.text:
            parts.append(node.text)
    flush()
    if not out:
        raise RuntimeError(f"No Greek verses extracted for {book} from {url}")
    return out

records = []
for book in HEBREW:
    records.extend(extract_hebrew(book))
for book in GREEK:
    records.extend(extract_greek(book))

if len(records) < 30000:
    raise RuntimeError(f"Corpus unexpectedly small ({len(records)} records); refusing to build an incomplete APK.")

out = ROOT / "verses.jsonl"
with out.open("w", encoding="utf-8", newline="\n") as handle:
    for record in records:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

notice = """OFFLINE CORPUS SOURCE NOTICES

HEBREW TEXT
Open Scriptures Hebrew Bible (OSHB), based on the Westminster Leningrad Codex (WLC).
The upstream project states that the WLC base text is public domain and the lemma/morphology annotations are CC BY 4.0. This app preserves attribution to the Open Scriptures Hebrew Bible Project.
Source: https://github.com/openscriptures/morphhb
These records are not Dead Sea Scrolls transcriptions.

GREEK TEXT
SBL Greek New Testament v1.2.
Copyright 2010 Society of Biblical Literature and Logos Bible Software; licensed CC BY 4.0.
Source: https://github.com/Faithlife/SBLGNT
This is a critically edited Greek text, not a diplomatic transcription of P46, P52, P66, P75, Codex Vaticanus, Codex Sinaiticus, or any single manuscript.

LIMITATIONS
This corpus is a starting text collection. It is not a complete manuscript archive, facsimile collection, or critical apparatus. Do not attribute a reading to an individual ancient witness without checking that witness at the specific passage. Hebrew and Greek source records retain their source references and attribution metadata.
"""
(ROOT / "SOURCE_NOTICES.txt").write_text(notice, encoding="utf-8")
print(f"Created {len(records)} attributed verse records.")
