#!/usr/bin/env python3
"""Extract line-level Hebrew-script OCR candidates from Cowley-Neubauer pages.

These are machine-generated candidate lines only. They retain page/line
coordinates and raw OCR text, and are never promoted to verified manuscript
readings or automatically aligned to Sirach verses.
"""
import json
import pathlib
import re

ROOT = pathlib.Path("app/src/main/assets")
SOURCE = ROOT / "corpus/sirach/cowley_neubauer_ms_b_pdf_pages.jsonl"
OUT = ROOT / "corpus/sirach/cowley_neubauer_ms_b_hebrew_line_candidates.jsonl"
INDEX = ROOT / "corpus/sirach/cowley_neubauer_ms_b_hebrew_line_candidates_index.json"


def main():
    if not SOURCE.exists():
        raise SystemExit("Cowley-Neubauer page OCR archive is missing")
    candidates = []
    page_count = 0
    with SOURCE.open(encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            page = json.loads(raw)
            page_count += 1
            for line_number, line in enumerate(page["ocr_text"].splitlines(), start=1):
                hebrew_count = len(re.findall(r"[\\u0590-\\u05FF]", line))
                if not hebrew_count:
                    continue
                candidates.append({
                    "writing_id": "sirach",
                    "witness_id": "Genizah-B",
                    "manuscript_id": "MS B",
                    "edition_source_id": "cowley-neubauer-1897-ms-b",
                    "pdf_page_number": page["pdf_page_number"],
                    "ocr_line_number": line_number,
                    "raw_ocr_line": line,
                    "hebrew_script_character_count": hebrew_count,
                    "text_status": "unverified_hebrew_script_OCR_candidate; not verse_aligned; not a verified manuscript reading",
                    "source_url": page["source_url"],
                    "source_sha256": page["source_sha256"],
                    "ocr_engine": page["ocr_engine"],
                    "ocr_language": page["ocr_language"],
                    "ocr_dpi": page["ocr_dpi"],
                    "license": page["license"]
                })
    if page_count < 40 or not candidates:
        raise SystemExit(f"Unexpected Cowley OCR candidate coverage: {page_count} pages, {len(candidates)} Hebrew-script lines")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\\n") as target:
        for row in candidates:
            target.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\\n")
    INDEX.write_text(json.dumps({
        "schema_version": 1,
        "record_type": "unverified_cowley_neubauer_ms_b_hebrew_script_ocr_line_candidates",
        "writing_id": "sirach",
        "witness_id": "Genizah-B",
        "manuscript_id": "MS B",
        "source_asset": "corpus/sirach/cowley_neubauer_ms_b_pdf_pages.jsonl",
        "candidate_asset": "corpus/sirach/cowley_neubauer_ms_b_hebrew_line_candidates.jsonl",
        "source_page_count": page_count,
        "candidate_line_count": len(candidates),
        "distinct_pdf_pages": len({row["pdf_page_number"] for row in candidates}),
        "text_status": "unverified OCR candidates only; no verse alignment; no normalization; no silent reconstruction",
        "limitations": [
            "OCR can confuse Hebrew letters, punctuation, brackets, dots, and column order.",
            "Some lines may mix Hebrew with English, Greek, Syriac, or editorial notes.",
            "Every candidate must be checked against the PDF facsimile before transcription use.",
            "Printed editorial restorations and marginal variants remain to be distinguished manually.",
            "This file is not a diplomatic transcription and must not be merged into the reconstructed Hebrew text."
        ]
    }, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Extracted {len(candidates)} unverified Hebrew-script OCR line candidates from {page_count} Cowley PDF pages.")


if __name__ == "__main__":
    main()
