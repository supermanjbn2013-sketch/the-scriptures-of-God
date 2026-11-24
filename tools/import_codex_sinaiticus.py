#!/usr/bin/env python3
"""Import the ITSEE Codex Sinaiticus XML as page/column/line-addressable offline text."""
import gzip
import json
import pathlib
import re
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/sinaiticus")
PAGES = ROOT / "pages"
SOURCE_REPO = "https://github.com/itsee-birmingham/codex-sinaiticus"
SOURCE_COMMIT = "af1633b5102cbe6200e79053cc618ac447e1bb16"
SOURCE_PATH = "sinaiticus_full_v195.xml"
SOURCE_URL = "https://raw.githubusercontent.com/itsee-birmingham/codex-sinaiticus/" + SOURCE_COMMIT + "/" + SOURCE_PATH
ATTRIBUTION = "Codex Sinaiticus Project electronic transcription; XML maintained by ITSEE, University of Birmingham. " + SOURCE_REPO
LICENSE = "CC BY-NC-SA 3.0 Unported"
USER_AGENT = "The-Scriptures-of-God-Archive/1.0"


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    xml_path = pathlib.Path(tempfile.gettempdir()) / SOURCE_PATH
    if not xml_path.exists() or xml_path.stat().st_size < 1_000_000:
        request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=180) as response, xml_path.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)

    pages, total_lines, total_words = [], 0, 0
    with xml_path.open("rb") as source:
        for event, page in ET.iterparse(source, events=("end",)):
            if lname(page.tag) != "page":
                continue
            page_id = page.attrib.get("id", "")
            if not page_id or not re.fullmatch(r"[A-Za-z0-9_.-]+", page_id):
                page.clear()
                continue
            page_records = []
            columns = set()
            for col in page.iter():
                if lname(col.tag) != "col":
                    continue
                col_id = col.attrib.get("id", "")
                for line in col:
                    if lname(line.tag) != "line":
                        continue
                    line_id = line.attrib.get("id", "")
                    words, word_ids = [], []
                    for word in line.iter():
                        if lname(word.tag) == "word":
                            value = "".join(word.itertext())
                            if value:
                                words.append(value)
                                word_ids.append(word.attrib.get("id", ""))
                    if not words and not word_ids:
                        continue
                    page_records.append({
                        "page_id": page_id,
                        "column_id": col_id,
                        "line_id": line_id,
                        "text": "".join(words),
                        "word_ids": word_ids
                    })
                    total_words += len(words)
                    columns.add(col_id)
            if page_records:
                safe_name = page_id + ".jsonl.gz"
                with gzip.open(PAGES / safe_name, "wt", encoding="utf-8", newline="\n", compresslevel=9) as out:
                    for record in page_records:
                        out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                pages.append({
                    "page_id": page_id,
                    "asset_file": "sinaiticus/pages/" + safe_name,
                    "column_ids": sorted(columns),
                    "column_count": len(columns),
                    "line_count": len(page_records)
                })
                total_lines += len(page_records)
            page.clear()

    if not pages or total_lines < 1000:
        raise SystemExit("Import rejected: unexpectedly small or empty transcription.")
    index = {
        "schema_version": 1,
        "record_type": "codex_sinaiticus_page_column_line_transcription",
        "manuscript": "Codex Sinaiticus",
        "language": "Greek",
        "source_revision": SOURCE_COMMIT,
        "source_file": SOURCE_PATH,
        "source_url": SOURCE_URL,
        "source_repository": SOURCE_REPO,
        "attribution": ATTRIBUTION,
        "license": LICENSE,
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/3.0/",
        "text_handling": "Diplomatic transcription text is retained as supplied; no spelling normalization or verse reconstruction is performed.",
        "coordinate_policy": "Original page, column, line, and word identifiers are preserved. No chapter-and-verse references are invented.",
        "page_count": len(pages),
        "line_count": total_lines,
        "word_count": total_words,
        "pages": pages
    }
    (ROOT / "sinaiticus_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(
        ATTRIBUTION + "\nLicense: " + LICENSE + "\n"
        "Non-commercial use only. Adaptations must be distributed under the same licence.\n"
        "Pinned source revision: " + SOURCE_COMMIT + "\n"
        "Original page, column, line, and word identifiers are preserved.\n",
        encoding="utf-8"
    )
    print(f"Imported {len(pages)} pages, {total_lines} lines, {total_words} word elements.")


if __name__ == "__main__":
    main()
