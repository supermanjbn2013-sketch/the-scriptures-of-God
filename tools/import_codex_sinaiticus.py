#!/usr/bin/env python3
"""Import ITSEE's TEI Codex Sinaiticus transcription as offline page files.

The current upstream XML uses TEI page/column/line milestones (pb/cb/lb),
not nested page/col/line elements. A legacy nested-layout reader is retained
for older project XML. Source wording and XML identifiers are not normalized.
"""
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
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
USER_AGENT = "The-Scriptures-of-God-Archive/1.0"


def lname(tag):
    return tag.rsplit("}", 1)[-1].lower()


def marker_id(elem, fallback=""):
    return elem.attrib.get(XML_ID) or elem.attrib.get("id") or elem.attrib.get("n") or elem.attrib.get("folionum") or fallback


def safe_file(value):
    if not value or not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        raise ValueError("Unsafe or missing source page identifier: " + repr(value))
    return value + ".jsonl.gz"


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

    pages = []
    total_lines = 0
    current_page = None
    current_column = ""
    current_line = ""
    page_handle = None
    page_counts = None
    tokens = []
    word_ids = []
    token_markup = []
    element_stack = []
    book_divisions = []
    word_depth = 0
    legacy_mode = False
    root_seen = False

    def finish_line():
        nonlocal total_lines, tokens, word_ids, token_markup
        if current_page is None or not tokens:
            tokens, word_ids, token_markup = [], [], []
            return
        record = {
            "page_id": current_page,
            "column_id": current_column,
            "line_id": current_line,
            "text": " ".join(tokens),
            "word_ids": word_ids,
            "token_markup": token_markup
        }
        page_handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        page_counts["line_count"] += 1
        total_lines += 1
        tokens, word_ids, token_markup = [], [], []

    def finish_page():
        nonlocal page_handle, page_counts
        if page_handle is not None:
            page_handle.close()
            if page_counts and page_counts["line_count"] > 0:
                pages.append(page_counts)
            page_handle = None
            page_counts = None

    def start_page(page_id):
        nonlocal current_page, current_column, current_line, page_handle, page_counts
        finish_line()
        finish_page()
        current_page = page_id
        current_column = ""
        current_line = ""
        if not current_page:
            return
        filename = safe_file(current_page)
        page_handle = gzip.open(PAGES / filename, "wt", encoding="utf-8", newline="\n", compresslevel=9)
        page_counts = {
            "page_id": current_page,
            "asset_file": "sinaiticus/pages/" + filename,
            "column_ids": [],
            "column_count": 0,
            "line_count": 0
        }

    with xml_path.open("rb") as source:
        for event, elem in ET.iterparse(source, events=("start", "end")):
            tag = lname(elem.tag)
            if event == "start" and not root_seen:
                root_seen = True
                legacy_mode = tag == "page"

            if legacy_mode:
                if event == "end" and tag == "page":
                    page_id = marker_id(elem)
                    start_page(page_id)
                    for col in elem.iter():
                        if lname(col.tag) != "col":
                            continue
                        col_id = marker_id(col)
                        if page_counts is not None and col_id and col_id not in page_counts["column_ids"]:
                            page_counts["column_ids"].append(col_id)
                        current_column = col_id
                        for line_elem in col:
                            if lname(line_elem.tag) != "line":
                                continue
                            current_line = marker_id(line_elem)
                            tokens, word_ids = [], []
                            for word in line_elem.iter():
                                if lname(word.tag) == "word":
                                    value = "".join(word.itertext())
                                    if value:
                                        tokens.append(value)
                                        word_ids.append(marker_id(word))
                            finish_line()
                    if page_counts is not None:
                        page_counts["column_count"] = len(page_counts["column_ids"])
                    finish_page()
                    elem.clear()
                continue

            if event == "start":
                element_stack.append({"element": tag, "attributes": dict(elem.attrib)})
                if tag == "div" and elem.attrib.get("type") == "book":
                    book_divisions.append({
                        "xml_id": elem.attrib.get(XML_ID),
                        "id": elem.attrib.get("id"),
                        "n": elem.attrib.get("n")
                    })
                if tag == "pb":
                    start_page(marker_id(elem))
                elif tag == "cb":
                    finish_line()
                    current_column = marker_id(elem)
                    if page_counts is not None and current_column and current_column not in page_counts["column_ids"]:
                        page_counts["column_ids"].append(current_column)
                elif tag == "lb":
                    finish_line()
                    current_line = marker_id(elem)
                elif tag == "w":
                    word_depth += 1
                continue

            if tag == "w":
                word_depth -= 1
                if word_depth == 0:
                    value = "".join(elem.itertext())
                    if value:
                        tokens.append(value)
                        word_ids.append(marker_id(elem))
                        token_markup.append({
                            "kind": "word",
                            "xml": ET.tostring(elem, encoding="unicode"),
                            "context": element_stack[:-1]
                        })
                    elem.clear()
            elif tag == "pc" and word_depth == 0:
                value = "".join(elem.itertext())
                if value:
                    tokens.append(value)
                    word_ids.append(marker_id(elem))
                    token_markup.append({
                        "kind": "punctuation",
                        "xml": ET.tostring(elem, encoding="unicode"),
                        "context": element_stack[:-1]
                    })
                elem.clear()
            if element_stack:
                element_stack.pop()

    finish_line()
    finish_page()
    if not pages or total_lines < 1000:
        raise SystemExit("Import rejected: unexpectedly small or empty transcription; check source XML structure.")

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
        "book_divisions": book_divisions,
        "page_count": len(pages),
        "line_count": total_lines,
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
    print(f"Imported {len(pages)} pages and {total_lines} manuscript lines.")
    print("Codex Sinaiticus book divisions: " + json.dumps(book_divisions, ensure_ascii=False))


if __name__ == "__main__":
    main()
