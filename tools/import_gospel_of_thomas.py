#!/usr/bin/env python3
"""Import the Coptic SCRIPTORIUM edition of the Gospel of Thomas.

The source is Paul Dilley's Coptic edition based on examination of the
Nag Hammadi Codex II facsimile. The import preserves codex page, column,
line, saying and paragraph identifiers. It does not reconstruct missing text.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/thomas")
REV = "e624efd798e3b49530472c7a4258db636222a826"
SOURCE_PATH = "thomas-gospel/thomas.gospel_TEI/thomas_gospel.xml"
SOURCE_URL = f"https://raw.githubusercontent.com/CopticScriptorium/corpora/{REV}/{SOURCE_PATH}"
REPO_URL = f"https://github.com/CopticScriptorium/corpora/tree/{REV}/thomas-gospel/thomas.gospel_TEI"
LICENSE = "CC BY 4.0"
ATTRIBUTION = ("Paul C. Dilley, ed., Gospel of Thomas, Coptic SCRIPTORIUM "
               "version 6.2.0 (2025-11-25), with annotations by Lydia "
               "Bremer-McCollum, Caroline T. Schroeder and Amir Zeldes; "
               "CC BY 4.0.")
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def clean(value):
    return re.sub(r"\\s+", " ", value or "").strip()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    source = ROOT / "thomas_source.xml"
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, source.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    tree = ET.parse(source)
    root = tree.getroot()
    records = []
    state = {"page": "", "column": "", "line": "", "saying": "", "paragraph": ""}
    tokens = []

    def flush():
        text = clean(" ".join(tokens))
        if text:
            records.append({
                "work": "Gospel of Thomas",
                "language": "cop",
                "dialect": "Sahidic Coptic with Lycopolitan features",
                "codex": "Nag Hammadi Codex II",
                "manuscript_id": "NH 10544",
                "page": state["page"],
                "column": state["column"],
                "line": state["line"],
                "saying": state["saying"],
                "paragraph": state["paragraph"],
                "reference": "Gospel of Thomas " + (state["saying"] or "prologue"),
                "text": text,
                "source_revision": REV,
                "source_url": SOURCE_URL,
                "license": LICENSE,
                "attribution": ATTRIBUTION,
                "textual_basis": "Coptic SCRIPTORIUM edition by Paul Dilley, based on examination of the Nag Hammadi Codex II facsimile; manuscript page/column/line identifiers retained."
            })
        tokens.clear()

    def walk(node):
        tag = lname(node.tag)
        if tag == "pb":
            flush()
            state["page"] = node.attrib.get(XML_ID, "").replace("NHAM02.", "")
            state["column"] = ""
            state["line"] = ""
            return
        if tag == "cb":
            flush()
            state["column"] = node.attrib.get("n", "")
            return
        if tag == "lb":
            flush()
            state["line"] = node.attrib.get("n", "")
            return
        if tag == "div1":
            flush()
            state["saying"] = node.attrib.get("n", "")
            for child in list(node):
                walk(child)
            flush()
            return
        if tag == "p":
            flush()
            state["paragraph"] = node.attrib.get("n", "")
            for child in list(node):
                walk(child)
            flush()
            return
        if tag == "w":
            word = clean("".join(node.itertext()))
            if word:
                tokens.append(word)
            return
        if tag in ("gap",):
            tokens.append("[lacuna]")
            return
        if node.text and clean(node.text):
            tokens.append(clean(node.text))
        for child in list(node):
            walk(child)
            if child.tail and clean(child.tail):
                tokens.append(clean(child.tail))

    body = next((x for x in root.iter() if lname(x.tag) == "body"), None)
    if body is None:
        raise SystemExit("Coptic SCRIPTORIUM TEI has no text body.")
    walk(body)
    flush()

    pages = sorted({int(r["page"]) for r in records if r["page"].isdigit()})
    sayings = sorted({int(r["saying"]) for r in records if r["saying"].isdigit()})
    lines = len(records)
    if len(pages) < 17 or pages[0] != 32 or pages[-1] != 51 or len(sayings) < 110 or lines < 500:
        raise SystemExit(f"Thomas import rejected: {len(pages)} pages, {len(sayings)} numbered sayings, {lines} line records.")

    with (ROOT / "thomas_coptic.jsonl").open("w", encoding="utf-8", newline="\n") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    index = {
        "schema_version": 1,
        "work": "Gospel of Thomas",
        "language": "Sahidic Coptic with Lycopolitan features",
        "manuscript": "Nag Hammadi Codex II, tractate 2, pages 32–51",
        "manuscript_id": "Coptic Museum, Cairo, NH 10544",
        "page_count": len(pages),
        "pages": pages,
        "codex_page_range": [32, 51],
        "line_record_count": lines,
        "sayings_in_source": sayings,
        "source_revision": REV,
        "source_url": SOURCE_URL,
        "repository_url": REPO_URL,
        "edition": "Paul C. Dilley, ed., Coptic SCRIPTORIUM version 6.2.0 (2025-11-25)",
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "status": "Imported offline as page-, column- and line-indexed Coptic text.",
        "limitations": [
            "The complete surviving copy is in Sahidic Coptic in Nag Hammadi Codex II; the work is commonly understood to have been composed originally in Greek.",
            "This is a scholarly digital edition based on examination of the facsimile, not a new independent transcription made by this app.",
            "The app preserves the source edition's codex page, column, line and saying references.",
            "The three Greek Oxyrhynchus fragments (P.Oxy. 1, 654 and 655) are separate witnesses and are not included in this Coptic dataset.",
            "Damaged, missing or unreadable wording is not reconstructed.",
            "Nag Hammadi manuscript images are not bundled; institutional image rights remain separate."
        ],
        "asset_file": "other_reference/thomas/thomas_coptic.jsonl"
    }
    (ROOT / "thomas_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(ATTRIBUTION + "\nLicense: " + LICENSE + "\nSource: " + SOURCE_URL + "\n", encoding="utf-8")
    print(f"Imported Gospel of Thomas Coptic text: {len(pages)} codex pages, {lines} page/column/line records, {len(sayings)} numbered sayings (CC BY 4.0).")


if __name__ == "__main__":
    main()
