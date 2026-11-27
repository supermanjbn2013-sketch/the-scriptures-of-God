#!/usr/bin/env python3
"""Import the currently transcribed David Kahana Hebrew Ben Sira edition.

This preserves Kahana's square brackets. In the Wikisource transcription,
bracketed Hebrew in passages whose Hebrew manuscript text is absent is an
editorial Hebrew retroversion from Greek/Syriac, not an ancient Hebrew witness.
The source page is marked incomplete, so this importer never claims full coverage.
"""
import json
import pathlib
import re
import urllib.parse
import urllib.request

OUT = pathlib.Path("app/src/main/assets/corpus/sirach/kahana_1912_hebrew.jsonl")
INDEX = pathlib.Path("app/src/main/assets/corpus/sirach/kahana_1912_index.json")
PAGE = "בן סירא (מהדורת דוד כהנא)"
API = "https://he.wikisource.org/w/api.php"
SOURCE_URL = "https://he.wikisource.org/wiki/" + urllib.parse.quote(PAGE.replace(" ", "_"))
UA = "TheScripturesOfGodCorpus/1.0 (source attribution and text research)"


def fetch_page():
    query = urllib.parse.urlencode({
        "action": "parse", "page": PAGE, "prop": "text", "format": "json",
        "disablelimitreport": "1"
    })
    request = urllib.request.Request(API + "?" + query, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    html = payload.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        raise RuntimeError("Wikisource returned no parsed page text")
    return html


from html.parser import HTMLParser


class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.current = None
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style", "sup"):
            self.skip += 1
        if self.skip:
            return
        if tag in ("p", "h2", "h3", "h4", "li"):
            if self.current is not None and self.current.strip():
                self.blocks.append(self.current.strip())
            self.current = ""
        elif tag == "br" and self.current is not None:
            self.current += "\n"

    def handle_endtag(self, tag):
        if tag in ("script", "style", "sup") and self.skip:
            self.skip -= 1
            return
        if self.skip:
            return
        if tag in ("p", "h2", "h3", "h4", "li"):
            if self.current is not None and self.current.strip():
                self.blocks.append(self.current.strip())
            self.current = None

    def handle_data(self, data):
        if not self.skip and self.current is not None:
            self.current += data


HEBREW_NUMERALS = {
    "א":1,"ב":2,"ג":3,"ד":4,"ה":5,"ו":6,"ז":7,"ח":8,"ט":9,
    "י":10,"כ":20,"ך":20,"ל":30,"מ":40,"ם":40,"נ":50,"ן":50,
    "ס":60,"ע":70,"פ":80,"ף":80,"צ":90,"ץ":90,"ק":100,
    "ר":200,"ש":300,"ת":400
}


def gematria(value):
    value = value.replace("׳", "").replace("״", "").replace("'", "").replace('"', "")
    return sum(HEBREW_NUMERALS.get(ch, 0) for ch in value)


VERSE = re.compile(r"(?<!\S)\(\*?([א-ת][א-ת׳״']*)\)\s*")


def main():
    parser = Blocks()
    parser.feed(fetch_page())
    chapter = None
    records = []
    for block in parser.blocks:
        heading = re.search(r"פרק\s+([א-ת׳״']+)", block)
        if heading:
            chapter = gematria(heading.group(1))
            continue
        if chapter is None:
            continue
        matches = list(VERSE.finditer(block))
        if not matches:
            continue
        for i, match in enumerate(matches):
            raw = block[match.end():matches[i+1].start() if i+1 < len(matches) else len(block)].strip()
            raw = re.sub(r"\s+", " ", raw).strip()
            if not raw:
                continue
            bracketed = raw.startswith("[") and raw.endswith("]")
            contains_bracketed_material = "[" in raw or "]" in raw
            records.append({
                "writing_id": "sirach",
                "chapter": chapter,
                "verse_label": match.group(1),
                "verse_number": gematria(match.group(1).lstrip("*")),
                "text": raw,
                "source_id": "kahana-ben-sira-1912",
                "source_edition": "David Kahana, Ben Sira, Warsaw 1912; Wikisource transcription",
                "source_url": SOURCE_URL,
                "transcription_status": "online_transcription_in_progress",
                "editorial_status": (
                    "bracketed_hebrew_retroversion_from_greek_and_or_syriac"
                    if bracketed else
                    "kahana_edition_contains_bracketed_editorial_retroversion"
                    if contains_bracketed_material else
                    "kahana_hebrew_edition_based_on_manuscript_evidence_not_a_diplomatic_single_witness"
                ),
                "direct_manuscript_witness": False,
                "preserve_brackets": True,
                "license": "1912 edition public domain; Wikisource transcription CC BY-SA 4.0"
            })
    if not records:
        raise RuntimeError("No numbered Ben Sira verses parsed; refusing to create an empty corpus")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as target:
        for record in records:
            target.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    chapters = sorted({r["chapter"] for r in records})
    chapter_record_counts = {
        str(chapter): sum(1 for record in records if record["chapter"] == chapter)
        for chapter in chapters
    }
    chapters_without_online_text = sorted(set(range(1, 52)) - set(chapters))
    fully_bracketed = sum(r["editorial_status"] == "bracketed_hebrew_retroversion_from_greek_and_or_syriac" for r in records)
    partially_bracketed = sum(r["editorial_status"] == "kahana_edition_contains_bracketed_editorial_retroversion" for r in records)
    bracketed = fully_bracketed + partially_bracketed
    INDEX.write_text(json.dumps({
        "schema_version": 1,
        "record_type": "sirach_kahana_1912_hebrew_edition_import",
        "source_id": "kahana-ben-sira-1912",
        "source_url": SOURCE_URL,
        "records": len(records),
        "chapters_with_online_text": chapters,
        "chapters_without_online_text": chapters_without_online_text,
        "chapter_record_counts": chapter_record_counts,
        "bracketed_retroversion_records": bracketed,
        "fully_bracketed_retroversion_records": fully_bracketed,
        "partially_bracketed_retroversion_records": partially_bracketed,
        "unbracketed_kahana_edition_records": len(records) - bracketed,
        "source_page_status": "Wikisource explicitly marks this transcription as incomplete",
        "limitations": [
            "This is Kahana's 1912 printed Hebrew edition, not a direct diplomatic transcription of a single ancient manuscript.",
            "Square-bracketed passages are editorial Hebrew retroversions where the Hebrew manuscript original was absent.",
            "Unbracketed readings are not assigned to a named manuscript without passage-level verification.",
            "Absence from the online transcription is not proof of an ancient manuscript lacuna.",
            "The import preserves Kahana's Hebrew text and editorial status; it does not claim that every chapter or verse is present."
        ]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(records)} Kahana Hebrew verse records across {len(chapters)} chapters; {bracketed} explicitly bracketed retroversions; online transcription has no text for chapters {chapters_without_online_text}.")


if __name__ == "__main__":
    main()
