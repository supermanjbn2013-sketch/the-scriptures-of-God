#!/usr/bin/env python3
"""Import Sefaria's separately identified David Kahana Hebrew Ben Sira version.

This is kept separate from the Wikisource transcription importer. The Sefaria
version is a digitization of Kahana's 1912 edition, not an ancient manuscript.
The importer records the exact version title and checks the API response so a
different/default Hebrew version cannot silently replace it.
"""
import html
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path("app/src/main/assets")
OUT = ROOT / "corpus/sirach/kahana_sefaria_hebrew.jsonl"
INDEX = ROOT / "corpus/sirach/kahana_sefaria_index.json"
BOOK = "Ben_Sira"
VERSION_TITLE = "Ben Sira, David Kahana ed. -- Wikisource"
VHE_PARAMETER = "hebrew|Ben_Sira,_David_Kahana_ed._--_Wikisource"
TEXT_API = "https://www.sefaria.org/api/texts/"
PAGE_URL = "https://www.sefaria.org/Ben_Sira.1?lang=bi&vhe=hebrew%7CBen_Sira%2C_David_Kahana_ed._--_Wikisource"
LICENSE = "CC BY-SA (version not specified in Sefaria's version metadata)"
UA = "TheScripturesOfGodCorpus/1.0 (source attribution and text research)"


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def clean_markup(value):
    value = str(value or "")
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"</p\s*>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def flatten_segments(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from flatten_segments(item)


def main():
    records = []
    chapter_counts = {}
    chapters_without_text = []
    version_source = None
    for chapter in range(1, 52):
        params = urllib.parse.urlencode({
            "context": "0",
            "commentary": "0",
            "vhe": VHE_PARAMETER
        })
        url = f"{TEXT_API}{BOOK}.{chapter}?{params}"
        data = fetch_json(url)
        returned_title = data.get("heVersionTitle") or data.get("versionTitle")
        if returned_title and "Kahana" not in str(returned_title):
            raise RuntimeError(
                f"Sefaria returned a different Hebrew version for chapter {chapter}: {returned_title!r}"
            )
        if returned_title and VERSION_TITLE not in str(returned_title) and "Kahana" not in str(returned_title):
            raise RuntimeError(f"Sefaria version title mismatch: {returned_title!r}")
        if chapter == 1:
            version_source = data.get("heVersionSource") or data.get("versionSource")
            if returned_title is None:
                raise RuntimeError("Sefaria did not identify the selected Hebrew version in its API response")
        hebrew = data.get("he")
        if isinstance(hebrew, str):
            hebrew = [hebrew]
        if not isinstance(hebrew, list):
            hebrew = []
        chapter_records = 0
        for verse_number, raw in enumerate(hebrew, start=1):
            raw_values = list(flatten_segments(raw))
            if not raw_values:
                continue
            raw_markup = " ".join(str(x) for x in raw_values)
            text = clean_markup(raw_markup)
            if not text:
                continue
            bracketed = text.startswith("[") and text.endswith("]")
            contains_brackets = "[" in text or "]" in text
            if bracketed:
                editorial_status = "bracketed_hebrew_retroversion_in_kahana_edition"
            elif contains_brackets:
                editorial_status = "kahana_edition_text_contains_editorial_bracketed_material"
            else:
                editorial_status = "kahana_edition_based_on_hebrew_manuscripts_not_a_diplomatic_single_witness"
            records.append({
                "writing_id": "sirach",
                "ref": f"Sirach {chapter}:{verse_number}",
                "chapter": chapter,
                "verse_number": verse_number,
                "text": text,
                "source_markup": raw_markup,
                "source_id": "sefaria-kahana-ben-sira",
                "source": "Sefaria digital text",
                "edition": VERSION_TITLE,
                "requested_version_parameter": VHE_PARAMETER,
                "printed_edition": "David Kahana, Ben Sira, Warsaw: Tushiyah, 1912",
                "version_source": version_source,
                "source_url": PAGE_URL,
                "api_source_url": url,
                "editorial_status": editorial_status,
                "direct_manuscript_witness": False,
                "license": LICENSE,
                "attribution": "David Kahana, ed., Ben Sira (1912); digitization by Sefaria; source transcription credited by Sefaria to Wikisource.",
                "source_text_status": "separate_Sefaria_digitization_of_Kahana_edition_not_an_ancient_manuscript"
            })
            chapter_records += 1
        chapter_counts[str(chapter)] = chapter_records
        if chapter_records == 0:
            chapters_without_text.append(chapter)
        time.sleep(0.05)

    if len(records) < 500 or len([n for n in chapter_counts.values() if n]) < 40:
        raise RuntimeError(
            f"Unexpectedly incomplete Sefaria Kahana import: {len(records)} records, "
            f"{sum(1 for n in chapter_counts.values() if n)} chapters"
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as target:
        for record in records:
            target.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    INDEX.write_text(json.dumps({
        "schema_version": 1,
        "record_type": "sirach_sefaria_kahana_hebrew_edition",
        "source_id": "sefaria-kahana-ben-sira",
        "source_url": PAGE_URL,
        "api_source": TEXT_API + BOOK,
        "version_title": VERSION_TITLE,
        "requested_version_parameter": VHE_PARAMETER,
        "version_source": version_source,
        "license": LICENSE,
        "verse_record_count": len(records),
        "chapter_count_with_text": sum(1 for n in chapter_counts.values() if n),
        "chapter_counts": chapter_counts,
        "chapters_without_text_in_this_version": chapters_without_text,
        "limitations": [
            "This is a Sefaria digitization of David Kahana's 1912 Hebrew edition, not an ancient manuscript.",
            "Kahana's edition combines Hebrew manuscript-based readings with editorial Hebrew retroversions where Hebrew manuscript text was absent.",
            "Unbracketed Kahana text is not assigned to one named Genizah manuscript without passage-level verification.",
            "The source's displayed license is CC-BY-SA without a version number; the asset retains that uncertainty.",
            "The importer explicitly requests the named Kahana version and refuses a different/default version.",
            "Missing text in this digital version is not proof of an ancient manuscript lacuna."
        ]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(records)} Sefaria Kahana Hebrew verse records across {sum(1 for n in chapter_counts.values() if n)} chapters.")


if __name__ == "__main__":
    main()
