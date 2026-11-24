#!/usr/bin/env python3
"""Import both Greek recensions of the Testament of Abraham from First1KGreek.

The two recensions remain separate. This is an edition-derived Greek text
edited by M. R. James, not a direct diplomatic transcription of one codex.
Source page markers, manuscript-variant notes and editorial deletions are
retained; no missing wording is reconstructed.
"""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/testament_abraham")
REV = "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
LICENSE = "CC BY-SA 4.0"
SOURCES = {
    "A": {
        "path": "data/tlg1701/tlg001/tlg1701.tlg001.1st1K-grc1.xml",
        "edition": "M. R. James, Testament of Abraham, Recension A",
    },
    "B": {
        "path": "data/tlg1701/tlg002/tlg1701.tlg002.1st1K-grc1.xml",
        "edition": "M. R. James, Testament of Abraham, Recension B",
    },
}


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def clean_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_recension(name, spec):
    source_url = f"https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/{REV}/{spec['path']}"
    local = ROOT / f"testament_abraham_{name}_source.xml"
    request = urllib.request.Request(source_url, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, local.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    root = ET.parse(local).getroot()
    edition = next((e for e in root.iter() if lname(e.tag) == "div" and e.attrib.get("type") == "edition"), None)
    if edition is None:
        raise SystemExit(f"Testament of Abraham Recension {name}: edition division missing.")

    title = ""
    records = []
    current_page = ""
    for child in list(edition):
        tag = lname(child.tag)
        if tag == "head":
            title = clean_space("".join(child.itertext()))
            continue
        if tag == "pb":
            current_page = child.attrib.get("n", current_page)
            continue
        if tag != "div" or child.attrib.get("subtype") != "chapter":
            continue

        chapter = child.attrib.get("n", "")
        if not chapter:
            continue
        pages = [current_page] if current_page else []
        notes = []
        line_markers = []
        chunks = []

        def walk(node):
            tag = lname(node.tag)
            if tag == "note":
                note_text = clean_space("".join(node.itertext()))
                if note_text:
                    notes.append({"type": node.attrib.get("type", ""), "number": node.attrib.get("n", ""), "text": note_text})
                return
            if tag == "pb":
                page = node.attrib.get("n", "")
                if page:
                    if page not in pages:
                        pages.append(page)
                    nonlocal_page[0] = page
                return
            if tag == "lb":
                marker = node.attrib.get("n", "")
                if marker:
                    line_markers.append(marker)
                    chunks.append(f" ⟦line {marker}⟧ ")
                return
            if node.text:
                chunks.append(node.text)
            for sub in list(node):
                subtag = lname(sub.tag)
                if subtag == "del":
                    deleted = clean_space("".join(sub.itertext()))
                    if deleted:
                        chunks.append(f" ⟦deleted: {deleted}⟧ ")
                elif subtag == "supplied":
                    supplied = clean_space("".join(sub.itertext()))
                    if supplied:
                        chunks.append(f"[{supplied}]")
                else:
                    walk(sub)
                if sub.tail:
                    chunks.append(sub.tail)

        nonlocal_page = [current_page]
        for node in list(child):
            walk(node)
        current_page = nonlocal_page[0]
        text = clean_space("".join(chunks))
        if not text:
            continue
        records.append({
            "work": "Testament of Abraham",
            "recension": name,
            "recension_title": f"Recension {name}",
            "chapter": int(chapter),
            "reference": f"Testament of Abraham, Recension {name}, chapter {chapter}",
            "language": "grc",
            "text": text,
            "source_pages": pages,
            "line_markers": line_markers,
            "editorial_notes_and_variants": notes,
            "edition": spec["edition"],
            "source_revision": REV,
            "source_url": source_url,
            "license": LICENSE,
            "attribution": f"Testament of Abraham, Recension {name}, edited by M. R. James; digital TEI by Open Greek and Latin / First1KGreek, CC BY-SA 4.0.",
            "textual_basis": "Printed Greek edition based on a manuscript tradition; not a direct diplomatic transcription of one manuscript."
        })

    if len(records) < 10:
        raise SystemExit(f"Testament of Abraham Recension {name}: unexpectedly small import ({len(records)} chapters).")
    return title, records, source_url


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    index_recensions = []
    for name, spec in SOURCES.items():
        title, records, source_url = parse_recension(name, spec)
        out_path = ROOT / f"recension_{name}_greek.jsonl"
        with out_path.open("w", encoding="utf-8", newline="\n") as out:
            for record in records:
                out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        index_recensions.append({
            "recension": name,
            "title": title,
            "edition": spec["edition"],
            "chapter_count": len(records),
            "asset_file": f"other_reference/testament_abraham/recension_{name}_greek.jsonl",
            "source_url": source_url
        })

    index = {
        "schema_version": 1,
        "work": "Testament of Abraham",
        "language": "Ancient Greek",
        "recensions": index_recensions,
        "edition": "M. R. James, Testament of Abraham, Greek Recensions A and B",
        "textual_basis": "Two distinct printed Greek recensions; not a direct diplomatic transcription of one manuscript.",
        "source_revision": REV,
        "license": LICENSE,
        "attribution": "M. R. James, Testament of Abraham, Recensions A and B; digital TEI by Open Greek and Latin / First1KGreek, CC BY-SA 4.0.",
        "limitations": [
            "Recensions A and B are separate textual forms and are never merged.",
            "The source is an edition-derived Greek text, not a direct diplomatic transcription of one manuscript.",
            "Source page markers, manuscript-variant notes, line markers and editorial deletions are retained.",
            "The digital transcription and encoding are distributed under CC BY-SA 4.0.",
            "No missing wording is reconstructed."
        ]
    }
    (ROOT / "testament_abraham_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(index["attribution"] + "\nLicense: " + LICENSE + "\nRevision: " + REV + "\n", encoding="utf-8")
    print("Imported Testament of Abraham: " + ", ".join(f"Recension {x['recension']} {x['chapter_count']} chapters" for x in index_recensions) + " (CC BY-SA 4.0).")


if __name__ == "__main__":
    main()
