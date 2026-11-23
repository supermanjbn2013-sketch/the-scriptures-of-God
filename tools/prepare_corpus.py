#!/usr/bin/env python3
"""Build the attributed offline corpus from openly licensed ancient-language editions."""
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/corpus")
ROOT.mkdir(parents=True, exist_ok=True)
HEBREW = ["Gen","Exod","Lev","Num","Deut","Josh","Judg","Ruth","1Sam","2Sam","1Kgs","2Kgs","1Chr","2Chr","Ezra","Neh","Esth","Job","Ps","Prov","Eccl","Song","Isa","Jer","Lam","Ezek","Dan","Hos","Joel","Amos","Obad","Jonah","Mic","Nah","Hab","Zeph","Hag","Zech","Mal"]
GREEK = ["Matt","Mark","Luke","John","Acts","Rom","1Cor","2Cor","Gal","Eph","Phil","Col","1Thess","2Thess","1Tim","2Tim","Titus","Phlm","Heb","Jas","1Pet","2Pet","1John","2John","3John","Jude","Rev"]
# Swete/First1KGreek digital files. Each file is an edited Septuagint text,
# not a diplomatic transcription of one surviving codex.
APOCRYPHA = [
    ("17.Esdras_A.txt", "1 Esdras", "1 Esdras (Greek)", "Greek Septuagint; Swete edition"),
    ("20.Judith.txt", "Judith", "Judith (Greek)", "Greek Septuagint; Swete edition"),
    ("21.Tobias.txt", "Tobit", "Tobit (Greek)", "Greek Septuagint; Swete edition; the book circulated in more than one Greek form"),
    ("19.Esther.txt", "Esther (Greek)", "Esther (Greek)", "Greek Esther text including its Greek expansions; Swete edition"),
    ("33.Sapientia_Salomonis.txt", "Wisdom of Solomon", "Wisdom of Solomon (Greek)", "Greek Septuagint; Swete edition"),
    ("34.Ecclesiasticus.txt", "Sirach", "Sirach (Greek)", "Greek Septuagint; Swete edition; Greek text does not replace surviving Hebrew witnesses"),
    ("50.Baruch.txt", "Baruch", "Baruch (Greek)", "Greek Septuagint; Swete edition"),
    ("52.Epistula_Jeremiae.txt", "Letter of Jeremiah", "Letter of Jeremiah (Greek)", "Greek Septuagint; Swete edition; also transmitted as Baruch chapter 6 in some arrangements"),
    ("23.Machabaeorum_i.txt", "1 Maccabees", "1 Maccabees (Greek)", "Greek Septuagint; Swete edition"),
    ("24.Machabaeorum_ii.txt", "2 Maccabees", "2 Maccabees (Greek)", "Greek Septuagint; Swete edition"),
    ("25.Machabaeorum_iii.txt", "3 Maccabees", "3 Maccabees (Greek)", "Greek Septuagint; Swete edition"),
    ("26.Machabaeorum_iv.txt", "4 Maccabees", "4 Maccabees (Greek)", "Greek Septuagint; Swete edition; placement varies among collections"),
    ("54.Susanna_translatio_Graeca.txt", "Susanna (Old Greek)", "Susanna (Old Greek)", "Old Greek form of Susanna; Swete edition"),
    ("55.Susanna_Theodotionis_versio.txt", "Susanna (Theodotion)", "Susanna (Theodotion)", "Theodotionic form of Susanna; separate from Old Greek"),
    ("56.Daniel_translatio_Graeca.txt", "Daniel (Old Greek)", "Daniel (Old Greek)", "Old Greek Daniel; separate Greek textual form"),
    ("57.Daniel_Theodotionis_versio.txt", "Daniel (Theodotion)", "Daniel (Theodotion)", "Theodotionic Daniel; separate Greek textual form"),
    ("58.Bel_et_Draco_translatio_Graeca.txt", "Bel and the Dragon (Old Greek)", "Bel and the Dragon (Old Greek)", "Old Greek form; separate from Theodotion"),
    ("59.Bel_et_Draco_Theodotionis_versio.txt", "Bel and the Dragon (Theodotion)", "Bel and the Dragon (Theodotion)", "Theodotionic form; separate from Old Greek"),
    ("28.Odae.txt", "Odes", "Odes (Greek collection)", "Greek collection of scriptural canticles; contents and individual compositions retain source numbering"),
    ("27.Psalmi.txt", "Psalm 151", "Psalm 151 (Greek)", "Greek Septuagint Psalter; Psalm 151 is an additional psalm, not part of the Hebrew WLC Psalter"),
]

LATIN_APOCRYPHA = [
    ("esdras2.txt", "2 Esdras / 4 Ezra (Latin)", "2 Esdras / 4 Ezra (Latin)",
     "Latin transmission of the composite 2 Esdras: 5 Ezra (chapters 1–2), 4 Ezra (chapters 3–14), and 6 Ezra (chapters 15–16). The source file includes 16 chapters; chapter 7 is checked for continuous verse numbering."),
    ("manasses.txt", "Prayer of Manasseh (Latin)", "Prayer of Manasseh (Latin)",
     "Latin Prayer of Manasseh as transmitted in the Vulgate appendix; not a claim that Latin is the original composition language.")
]
APOCRYPHA_EXTRACTS = [
    (8, 1, 15, "Prayer of Manasseh (Greek)", "Prayer of Manasseh (Greek)",
     "Greek Prayer of Manasseh, separately indexed from Odes 8 in the Swete Odes collection.")
]
LATIN_LIBRARY_BASE = "https://raw.githubusercontent.com/cltk/lat_text_latin_library/master/bible/"
LATIN_LIBRARY_REPO = "https://github.com/cltk/lat_text_latin_library"
SWETE_BASE = "https://raw.githubusercontent.com/nathans/lxx-swete/master/data/"
SWETE_REPO = "https://github.com/nathans/lxx-swete"
SWETE_LICENSE = "CC BY-SA 4.0"
SWETE_ATTRIBUTION = "Henry Barclay Swete, ed., The Old Testament in Greek according to the Septuagint; digital transcription from Open Greek and Latin First1KGreek via nathans/lxx-swete. https://github.com/nathans/lxx-swete"

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
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
        tokens = [node.text for node in verse.iter() if local_name(node.tag) == "w" and node.text]
        text = clean(tokens)
        if text:
            out.append({"ref": ref, "language": "he", "text": text,
                "source": "Open Scriptures Hebrew Bible (OSHB), based on the Westminster Leningrad Codex",
                "edition": "OSHB repository, wlc XML", "witness_basis": "Westminster Leningrad Codex",
                "transcription_type": "electronic edition text with OSHB annotations",
                "source_url": url, "text_status": "WLC base text is public domain; OSHB annotations CC BY 4.0",
                "attribution": "Open Scriptures Hebrew Bible Project: https://github.com/openscriptures/morphhb"})
    if not out:
        raise RuntimeError(f"No Hebrew verses extracted for {book} from {url}")
    return out

def extract_greek(book):
    url = f"https://raw.githubusercontent.com/Faithlife/SBLGNT/master/data/sblgnt/xml/{book}.xml"
    root = ET.fromstring(fetch(url))
    out, current_ref, parts = [], None, []
    def flush():
        if current_ref and parts:
            verse_text = clean(parts)
            if verse_text:
                out.append({"ref": current_ref, "language": "grc", "text": verse_text,
                    "source": "SBL Greek New Testament v1.2", "edition": "SBLGNT v1.2",
                    "witness_basis": "Critically edited Greek text; not a single manuscript transcription",
                    "transcription_type": "edited Greek text", "source_url": url, "license": "CC BY 4.0",
                    "attribution": "SBL Greek New Testament, © 2010 Society of Biblical Literature and Logos Bible Software. https://github.com/Faithlife/SBLGNT"})
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

def extract_swete(filename, title, book_code, witness_note):
    url = SWETE_BASE + filename
    raw = fetch(url).decode("utf-8-sig")
    # First1KGreek's Swete files encode each word as book.chapter.verse + token.
    # Group by the complete source reference; preserve the printed word order and marks.
    grouped = {}
    for line_no, line in enumerate(raw.splitlines(), 1):
        match = re.match(r"^([0-9]+\.[A-Za-z0-9]+\.[0-9]+)\s+(.+?)\s*$", line)
        if not match:
            continue
        ref, token = match.groups()
        grouped.setdefault(ref, []).append(token)
    out = []
    for ref, tokens in grouped.items():
        text = clean(tokens)
        if text:
            parts = ref.split(".")
        display_ref = ref
        if len(parts) == 3:
            chapter, verse = parts[1], parts[2]
            if title == "Psalm 151":
                display_ref = f"{title}:{verse}"
            else:
                if title == "Letter of Jeremiah" and chapter == "0":
                    chapter = "1"
                display_ref = f"{title} {chapter}:{verse}"
        out.append({"ref": display_ref, "source_reference": ref, "book": title, "book_code": book_code,
                "language": "grc", "text": text, "source": "Swete Septuagint (First1KGreek digital transcription)",
                "edition": "Henry Barclay Swete, The Old Testament in Greek according to the Septuagint",
                "witness_basis": "Edited Septuagint text; not a diplomatic transcription of one manuscript",
                "textual_form": witness_note, "transcription_type": "digitized edited Greek edition",
                "source_url": url, "repository": SWETE_REPO, "license": SWETE_LICENSE,
                "attribution": SWETE_ATTRIBUTION,
                "text_status": "Complete text as represented by this source file; source edition and textual form are identified separately from ancient manuscript witnesses."})
    if not out:
        raise RuntimeError(f"No verse records extracted for {title} from {url}")
    return out

def extract_latin_library(filename, title, book_code, textual_form):
    url = LATIN_LIBRARY_BASE + filename
    raw = fetch(url).decode("utf-8-sig")
    chapters = list(re.finditer(r"(?im)^\s*CAPUT\s+(\d+)\b", raw))
    if not chapters:
        raise RuntimeError(f"No chapter headings found for {title} from {url}")
    out = []
    chapter_numbers = []
    for index, chapter_match in enumerate(chapters):
        chapter = int(chapter_match.group(1))
        chapter_numbers.append(chapter)
        start = chapter_match.end()
        end = chapters[index + 1].start() if index + 1 < len(chapters) else len(raw)
        body = raw[start:end]
        verse_matches = list(re.finditer(r"(?<!\S)(\d{1,3})(?=\s)", body))
        verse_numbers = [int(m.group(1)) for m in verse_matches]
        if not verse_numbers or verse_numbers != list(range(1, max(verse_numbers) + 1)):
            raise RuntimeError(f"Missing or irregular verse numbering in {title} chapter {chapter}: {verse_numbers[:5]} ... {verse_numbers[-5:]}")
        for verse_index, verse_match in enumerate(verse_matches):
            verse_start = verse_match.end()
            verse_end = verse_matches[verse_index + 1].start() if verse_index + 1 < len(verse_matches) else len(body)
            text = clean([body[verse_start:verse_end]])
            if not text:
                raise RuntimeError(f"Empty verse in {title} {chapter}:{verse_numbers[verse_index]}")
            out.append({"ref": f"{book_code} {chapter}:{verse_numbers[verse_index]}",
                "book": title, "book_code": book_code, "language": "la", "text": text,
                "source": "The Latin Library text collected by the Classical Language Toolkit (CLTK)",
                "edition": "Latin Library digital text; the source file does not identify a modern critical edition",
                "witness_basis": "Latin textual transmission; not an ancient manuscript transcription",
                "textual_form": textual_form, "transcription_type": "digital Latin edition text",
                "source_url": url, "repository": LATIN_LIBRARY_REPO,
                "license": "Public Domain (as stated by the Latin Library source; CLTK repository README directs users to its public-domain notice)",
                "attribution": "The Latin Library; collected in cltk/lat_text_latin_library. https://github.com/cltk/lat_text_latin_library",
                "text_status": "Complete chapter and verse text as represented by the source file; verify against a critical Latin edition before using it as a manuscript-level witness."})
    if chapter_numbers != list(range(1, max(chapter_numbers) + 1)):
        raise RuntimeError(f"Missing chapters in {title}: {chapter_numbers}")
    if title.startswith("2 Esdras") and not any(r["ref"] == f"{book_code} 7:139" for r in out):
        raise RuntimeError("The supplied 2 Esdras Latin text does not include chapter 7 through verse 139.")
    return out

records = []
for book in HEBREW:
    records.extend(extract_hebrew(book))
for book in GREEK:
    records.extend(extract_greek(book))
apocrypha_counts = {}
for filename, title, code, note in APOCRYPHA:
    rows = extract_swete(filename, title, code, note)
    # Psalm 151 is a single extra psalm; reject the file if its chapter is not represented.
    if code == "Psalm 151 (Greek)":
        rows = [r for r in rows if r.get("source_reference", "").split(".")[-2:-1] == ["151"]]
        if not rows:
            raise RuntimeError("Psalm 151 was not found in the Swete Psalms source; do not add a placeholder as text.")
    records.extend(rows)
    apocrypha_counts[title] = len(rows)
for filename, title, code, note in LATIN_APOCRYPHA:
    rows = extract_latin_library(filename, title, code, note)
    records.extend(rows)
    apocrypha_counts[title] = len(rows)
for source_chapter, first_verse, last_verse, title, code, note in APOCRYPHA_EXTRACTS:
    source_rows = extract_swete("28.Odae.txt", title, code, note)
    rows = []
    for row in source_rows:
        parts = row["source_reference"].split(".")
        if len(parts) == 3 and parts[1] == str(source_chapter) and first_verse <= int(parts[2]) <= last_verse:
            row["ref"] = f"{code} 1:{int(parts[2]) - first_verse + 1}"
            rows.append(row)
    if not rows:
        raise RuntimeError(f"Could not extract complete Odes chapter {source_chapter} for {title}")
    records.extend(rows)
    apocrypha_counts[title] = len(rows)

if len(records) < 30000:
    raise RuntimeError(f"Corpus unexpectedly small ({len(records)} records); refusing to build an incomplete release.")
if len(apocrypha_counts) != len(APOCRYPHA) + len(LATIN_APOCRYPHA) + len(APOCRYPHA_EXTRACTS) or any(v == 0 for v in apocrypha_counts.values()):
    raise RuntimeError("One or more Apocrypha source books are missing or empty; refusing to build.")

out = ROOT / "verses.jsonl"
with out.open("w", encoding="utf-8", newline="\n") as handle:
    for record in records:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

notice = """OFFLINE CORPUS SOURCE NOTICES

HEBREW TEXT
Open Scriptures Hebrew Bible (OSHB), based on the Westminster Leningrad Codex (WLC).
WLC base text is public domain; OSHB annotations are CC BY 4.0. These records are not Dead Sea Scrolls transcriptions.
Source: https://github.com/openscriptures/morphhb

APOCRYPHA / DEUTEROCANONICAL GREEK TEXTS
Henry Barclay Swete, ed., The Old Testament in Greek according to the Septuagint.
Digital transcription: Open Greek and Latin First1KGreek, distributed through nathans/lxx-swete.
License: CC BY-SA 4.0. Preserve attribution and share-alike terms.
Source: https://github.com/nathans/lxx-swete
The imported texts are edited Greek editions, not diplomatic transcriptions of one ancient codex. Old Greek and Theodotionic forms of Daniel, Susanna, and Bel and the Dragon remain separate. Tobit's distinct Greek textual forms must not be conflated. The Greek text does not replace surviving Hebrew or Aramaic witnesses, including Dead Sea Scroll fragments.
The Odes file is a collection; its internal composition numbering is preserved. The Prayer of Manasseh (Odes 8, source verses 1–15) is also separately indexed while retaining its source references. Psalm 151 is imported separately from the Greek Psalter only when the source explicitly supplies chapter 151.
2 Esdras / 4 Ezra and the Prayer of Manasseh are also included from Latin Library digital texts collected by CLTK. The Latin text is a transmitted version, not the lost Greek or hypothesized Semitic original. 2 Esdras is a composite: 5 Ezra (chapters 1–2), 4 Ezra (chapters 3–14), and 6 Ezra (chapters 15–16). The source is checked for sequential chapter/verse numbering; it is not a critical edition or manuscript facsimile.\nSource: https://github.com/cltk/lat_text_latin_library (public-domain status stated by the Latin Library source).

APOSTOLIC WRITINGS
SBL Greek New Testament v1.2, CC BY 4.0.
Source: https://github.com/Faithlife/SBLGNT
This is a critically edited Greek text, not a diplomatic transcription of P46, P52, P66, P75, Codex Vaticanus, Codex Sinaiticus, or any single manuscript.

LIMITATIONS
This corpus is a research text collection, not a complete manuscript archive, facsimile collection, or critical apparatus. Do not attribute an edited reading to an individual ancient witness without checking that witness at the specific passage. Every record retains source, edition, language, licence, and transcription-type metadata.
"""
(ROOT / "SOURCE_NOTICES.txt").write_text(notice, encoding="utf-8")
(ROOT / "apocrypha_import_report.json").write_text(json.dumps(apocrypha_counts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Created {len(records)} attributed text records, including {sum(apocrypha_counts.values())} Apocrypha/Deuterocanonical records across {len(apocrypha_counts)} source files.")
