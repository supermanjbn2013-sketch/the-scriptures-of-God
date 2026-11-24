#!/usr/bin/env python3
"""Import the ITSEE Codex Sinaiticus XML as page/column/line-addressable offline text.

Source is pinned to a specific upstream commit. The XML is parsed without
normalizing Greek spelling, punctuation, accents, or editorial signs.
"""
import gzip
import json
import pathlib
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/sinaiticus")
SOURCE_REPO = "https://github.com/itsee-birmingham/codex-sinaiticus"
SOURCE_COMMIT = "af1633b5102cbe6200e79053cc618ac447e1bb16"
SOURCE_PATH = "sinaiticus_full_v195.xml"
SOURCE_URL = (
    "https://raw.githubusercontent.com/itsee-birmingham/codex-sinaiticus/"
    + SOURCE_COMMIT + "/" + SOURCE_PATH
)
ATTRIBUTION = (
    "Codex Sinaiticus Project, electronic transcription of Codex Sinaiticus; "
    "XML maintained by ITSEE, University of Birmingham. "
    + SOURCE_REPO
)
LICENSE = "CC BY-NC-SA 3.0 Unported"
USER_AGENT = "The-Scriptures-of-God-Archive/1.0 (offline corpus importer)"


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def word_text(node):
    return "".join(node.itertext())


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    xml_path = pathlib.Path(tempfile.gettempdir()) / SOURCE_PATH
    if not xml_path.exists() or xml_path.stat().st_size < 1_000_000:
        request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=180) as response, xml_path.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)

    pages = []
    total_lines = 0
    total_words = 0
    line_path = ROOT / "sinaiticus_lines.jsonl.gz"
    with xml_path.open("rb") as source, gzip.open(line_path, "wt", encoding="utf-8", newline="\n", compresslevel=9) as out:
        for event, elem in ET.iterparse(source, events=("end",)):
            if lname(elem.tag) != "page":
                continue
            page_id = elem.attrib.get("id", "")
            page_lines = 0
            page_columns = set()
            for line in elem.iter():
                if lname(line.tag) != "line":
                    continue
                line_id = line.attrib.get("id", "")
                parent_column = ""
                # The upstream XML nests line directly inside col.
                for col in elem.iter():
                    if lname(col.tag) == "col" and line in list(col):
                        parent_column = col.attrib.get("id", "")
                        break
                words = []
                word_ids = []
                for word in line.iter():
                    if lname(word.tag) == "word":
                        value = word_text(word)
                        if value:
                            words.append(value)
                            word_ids.append(word.attrib.get("id", ""))
                text = "".join(words)
                if not text and not word_ids:
                    continue
                record = {
                    "page_id": page_id,
                    "column_id": parent_column,
                    "line_id": line_id,
                    "text": text,
                    "word_ids": word_ids
                }
                out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                page_lines += 1
                total_lines += 1
                total_words += len(words)
                if parent_column:
                    page_columns.add(parent_column)
            if page_id:
                pages.append({
                    "page_id": page_id,
                    "column_ids": sorted(page_columns),
                    "column_count": len(page_columns),
                    "line_count": page_lines
                })
            elem.clear()

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
        "coordinate_policy": "Original page, column, line, and word identifiers are preserved. The transcription is not converted into invented chapter-and-verse references.",
        "page_count": len(pages),
        "line_count": total_lines,
        "word_count": total_words,
        "pages": pages
    }
    (ROOT / "sinaiticus_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "SOURCE_NOTICE.txt").write_text(
        ATTRIBUTION + "\nLicense: " + LICENSE + "\n"
        "Non-commercial use only. Adaptations must be distributed under the same licence.\n"
        "Source revision: " + SOURCE_COMMIT + "\n"
        "The original XML's manuscript coordinates and word identifiers are retained.\n",
        encoding="utf-8"
    )
    print(f"Imported {len(pages)} pages, {total_lines} lines, {total_words} word elements.")
    print(f"Compressed line corpus: {line_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
