#!/usr/bin/env python3
"""Extract the OCR text layer of Cowley & Neubauer's 1897 public-domain MS B edition.

This is a page-level source archive only. OCR text is not promoted to a
verse-level manuscript reading until it has been checked against the scan.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile
import urllib.request

ROOT = pathlib.Path("app/src/main/assets")
OUT = ROOT / "corpus/sirach/cowley_neubauer_ms_b_pdf_pages.jsonl"
INDEX = ROOT / "corpus/sirach/cowley_neubauer_ms_b_pdf_index.json"
URL = "https://upload.wikimedia.org/wikipedia/commons/8/8d/California_Digital_Library_%28IA_originalhebrewof00cowlrich%29.pdf"
TITLE = "A. E. Cowley and Adolf Neubauer, The Original Hebrew of a Portion of Ecclesiasticus (XXXIX.15–XLIX.11), Oxford, 1897"

def main():
    with tempfile.TemporaryDirectory() as temp:
        pdf_path = pathlib.Path(temp) / "cowley-neubauer-1897.pdf"
        text_path = pathlib.Path(temp) / "cowley-neubauer-1897.txt"
        request = urllib.request.Request(URL, headers={"User-Agent": "The-Scriptures-of-God/1.0 source archive"})
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "")
        if len(data) < 1_000_000 or b"%PDF" not in data[:1024]:
            raise RuntimeError(f"Unexpected Cowley-Neubauer PDF response: {len(data)} bytes; {content_type}")
        digest = hashlib.sha256(data).hexdigest()
        pdf_path.write_bytes(data)
        subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), str(text_path)],
            check=True
        )
        extracted = text_path.read_text(encoding="utf-8", errors="replace")

    pages = extracted.split("\f")
    rows = []
    hebrew_pages = []
    for page_number, page_text in enumerate(pages, start=1):
        if not page_text.strip():
            continue
        contains_hebrew = bool(re.search(r"[\u0590-\u05FF]", page_text))
        if contains_hebrew:
            hebrew_pages.append(page_number)
        rows.append({
            "writing_id": "sirach",
            "witness_id": "Genizah-B",
            "manuscript_id": "MS B",
            "edition_source_id": "cowley-neubauer-1897-ms-b",
            "pdf_page_number": page_number,
            "text": page_text,
            "contains_hebrew_script": contains_hebrew,
            "text_status": "raw_PDF_OCR_text_layer_not_verse_aligned_or_verified_against_facsimile",
            "source_title": TITLE,
            "source_url": URL,
            "source_sha256": digest,
            "license": "Public domain",
            "attribution": "A. E. Cowley and Adolf Neubauer, eds., The Original Hebrew of a Portion of Ecclesiasticus, Oxford: Clarendon Press, 1897."
        })

    if len(rows) < 40 or len(hebrew_pages) < 5:
        raise RuntimeError(
            f"Cowley-Neubauer PDF text extraction unexpectedly sparse: "
            f"{len(rows)} pages, {len(hebrew_pages)} pages containing Hebrew script."
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as target:
        for row in rows:
            target.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    INDEX.write_text(json.dumps({
        "schema_version": 1,
        "record_type": "cowley_neubauer_1897_ms_b_pdf_ocr_page_archive",
        "writing_id": "sirach",
        "witness_id": "Genizah-B",
        "manuscript_id": "MS B",
        "edition_source_id": "cowley-neubauer-1897-ms-b",
        "source_title": TITLE,
        "source_url": URL,
        "source_sha256": digest,
        "license": "Public domain",
        "attribution": "A. E. Cowley and Adolf Neubauer, eds., The Original Hebrew of a Portion of Ecclesiasticus, Oxford: Clarendon Press, 1897.",
        "pdf_page_count_extracted": len(rows),
        "pages_with_hebrew_script": hebrew_pages,
        "pages_with_hebrew_count": len(hebrew_pages),
        "coverage_as_printed": "Sirach 39:15–49:11",
        "asset": "corpus/sirach/cowley_neubauer_ms_b_pdf_pages.jsonl",
        "limitations": [
            "The printed edition is a scholarly transcription of direct Hebrew manuscript B, not the physical manuscript itself.",
            "This file contains raw PDF text-layer extraction only; it is not verse-aligned and must not be displayed as a verified manuscript reading.",
            "Printed brackets, dots, marginal variants, and parallel Greek/Syriac/English columns must be identified and kept separate.",
            "The PDF's OCR may contain Hebrew recognition errors; every verse-level reading must be checked against the page image or a reliable transcription.",
            "The printed edition covers only Sirach 39:15–49:11."
        ]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Extracted {len(rows)} Cowley-Neubauer PDF pages; "
        f"{len(hebrew_pages)} pages contain Hebrew script; SHA256={digest}"
    )
    for sample_page in hebrew_pages[:3]:
        sample = next(row for row in rows if row["pdf_page_number"] == sample_page)
        print(f"MS B OCR sample page {sample_page}: {sample['text'][:700]!r}")

if __name__ == "__main__":
    main()
