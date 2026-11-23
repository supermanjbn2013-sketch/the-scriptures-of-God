#!/usr/bin/env python3
"""Validate generated text corpus, Apocrypha imports, DSS metadata, and Android navigation."""
import json
import sys
import re
from pathlib import Path

ROOT = Path("app/src/main/assets")
rows = [json.loads(line) for line in (ROOT / "corpus/verses.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

REQUIRED_GREEK = {
    "1 Esdras", "Tobit", "Judith", "Esther (Greek)", "Wisdom of Solomon",
    "Sirach", "Baruch", "Letter of Jeremiah", "1 Maccabees", "2 Maccabees",
    "3 Maccabees", "4 Maccabees", "Susanna (Old Greek)", "Susanna (Theodotion)",
    "Daniel (Old Greek)", "Daniel (Theodotion)",
    "Bel and the Dragon (Old Greek)", "Bel and the Dragon (Theodotion)",
    "Odes", "Prayer of Manasseh (Greek)", "Psalm 151"
}
REQUIRED_LATIN = {"2 Esdras / 4 Ezra (Latin)", "Prayer of Manasseh (Latin)"}

HEBREW_BOOK_CODES = {
    "Gen","Exod","Lev","Num","Deut","Josh","Judg","Ruth","1Sam","2Sam","1Kgs","2Kgs",
    "1Chr","2Chr","Ezra","Neh","Esth","Job","Ps","Prov","Eccl","Song","Isa","Jer","Lam",
    "Ezek","Dan","Hos","Joel","Amos","Obad","Jonah","Mic","Nah","Hab","Zeph","Hag","Zech","Mal"
}
GREEK_BOOK_CODES = {
    "Matt","Mark","Luke","John","Acts","Rom","1Cor","2Cor","Gal","Eph","Phil","Col",
    "1Thess","2Thess","1Tim","2Tim","Titus","Phlm","Heb","Jas","1Pet","2Pet",
    "1John","2John","3John","Jude","Rev"
}

def validate_base():
    assert len(rows) >= 30000, f"Unexpected corpus size: {len(rows)}"
    assert all(r.get("ref") and r.get("text", "").strip() and r.get("source") for r in rows)
    hebrew = [r for r in rows if r["language"] == "he"]
    greek = [r for r in rows if r["language"] == "grc"]
    latin = [r for r in rows if r["language"] == "la"]
    assert hebrew and greek and latin
    assert all(r.get("source_url") and r.get("transcription_type") and r.get("edition") and r.get("witness_basis") for r in rows)
    assert all(r.get("book") and r.get("book_code") for r in greek + latin)
    hebrew_codes = {r["ref"].split(".", 1)[0] for r in hebrew}
    greek_codes = {r["book_code"] for r in greek if r["book_code"] in GREEK_BOOK_CODES}
    assert hebrew_codes == HEBREW_BOOK_CODES, f"Hebrew source book coverage mismatch: missing={HEBREW_BOOK_CODES - hebrew_codes}, unexpected={hebrew_codes - HEBREW_BOOK_CODES}"
    assert greek_codes == GREEK_BOOK_CODES, f"SBLGNT book coverage mismatch: missing={GREEK_BOOK_CODES - greek_codes}, unexpected={greek_codes - GREEK_BOOK_CODES}"
    assert all(r.get("attribution") for r in hebrew + greek + latin)
    refs = [(r["language"], r["ref"]) for r in rows]
    assert len(refs) == len(set(refs)), "Duplicate verse references detected within a language"
    print(f"Validated {len(rows)} text records; Hebrew {len(hebrew)} across {len(hebrew_codes)} books, Greek {len(greek)} across {len(greek_codes)} SBLGNT books, Latin {len(latin)}")

def validate_apocrypha():
    records = [r for r in rows if r.get("book")]
    books = {r["book"] for r in records}
    assert REQUIRED_GREEK.issubset(books), f"Missing Greek books/forms: {REQUIRED_GREEK - books}"
    assert REQUIRED_LATIN.issubset(books), f"Missing Latin books: {REQUIRED_LATIN - books}"
    greek = [r for r in records if r["language"] == "grc" and r["book"] in REQUIRED_GREEK]
    latin = [r for r in records if r["language"] == "la" and r["book"] in REQUIRED_LATIN]
    assert all(r.get("license") == "CC BY-SA 4.0" and r.get("textual_form") for r in greek)
    assert all(r.get("license", "").startswith("Public Domain") and r.get("textual_form") for r in latin)
    assert all(r.get("source_url") and r.get("attribution") for r in records)
    assert all(r.get("source_reference") for r in greek), "A Greek Apocrypha record is missing its original source coordinate"
    for book in REQUIRED_GREEK | REQUIRED_LATIN:
        assert any(r["book"] == book and r["text"].strip() for r in records), f"Empty text: {book}"
    report = json.loads((ROOT / "corpus/apocrypha_import_report.json").read_text(encoding="utf-8"))
    assert (REQUIRED_GREEK | REQUIRED_LATIN).issubset(set(report)), "Apocrypha import report is incomplete"
    coverage = json.loads((ROOT / "corpus/apocrypha_coverage.json").read_text(encoding="utf-8"))
    assert set(report).issubset(set(coverage)), "Apocrypha chapter coverage inventory is incomplete"
    for book, summary in coverage.items():
        book_rows = [r for r in records if r["book"] == book]
        assert summary["record_count"] == len(book_rows) == report[book], f"Record count mismatch: {book}"
        assert summary["chapter_count"] == len(summary["chapters"]) > 0, f"Chapter coverage missing: {book}"
        assert summary["source_url"] and summary["edition"] and summary["witness_basis"] and summary["scope_note"]
        source_refs = [r.get("source_reference") for r in book_rows]
        assert all(source_refs) and len(source_refs) == len(set(source_refs)), f"Missing or duplicate source coordinates: {book}"
        for chapter, details in summary["chapters"].items():
            verses = details["source_verse_numbers"]
            assert verses == sorted(set(verses)) and len(verses) == details["verse_count"]
            assert verses[0] == details["first_source_verse"] and verses[-1] == details["last_source_verse"]
    assert len(greek) >= 1000, f"Greek Apocrypha corpus unexpectedly small: {len(greek)}"
    assert len(latin) >= 150, f"Latin Apocrypha corpus unexpectedly small: {len(latin)}"
    assert any(r["ref"] == "2 Esdras / 4 Ezra (Latin) 7:139" for r in latin), "2 Esdras chapter 7 is incomplete"
    prayer = [r for r in records if r["book"] == "Prayer of Manasseh (Greek)"]
    assert len(prayer) == 15, f"Expected 15 Greek Prayer of Manasseh verses, found {len(prayer)}"
    assert all(r.get("source_reference", "").startswith("28.8.") for r in prayer)
    print(f"Validated {len(REQUIRED_GREEK | REQUIRED_LATIN)} complete Apocrypha books/forms; {len(records)} text records")

def validate_dss():
    dss = json.loads((ROOT / "catalog/dead_sea_scrolls_register.json").read_text(encoding="utf-8"))
    assert dss["record_type"] == "dead_sea_scrolls_manuscript_metadata_catalog"
    assert len(dss["records"]) >= 6
    ids = [r["id"] for r in dss["records"]]
    assert len(ids) == len(set(ids)), "Duplicate DSS catalogue IDs"
    for record in dss["records"]:
        assert record["name"] and record["language"] and record["date_estimate"]
        assert record["source_urls"] and record["status"] == "metadata catalogued; transcription not imported"
    concordance = json.loads((ROOT / "catalog/dss_passage_concordance.json").read_text(encoding="utf-8"))
    assert concordance["record_type"] == "dss_manuscript_passage_concordance"
    assert len(concordance["records"]) >= 5
    concordance_ids = [r["manuscript_id"] for r in concordance["records"]]
    assert len(concordance_ids) == len(set(concordance_ids))
    assert {"4Q26 Lev d", "4Q27 Num b", "4Q31 Deut d", "4Q47 Josh a", "4Q53 Sam c"}.issubset(set(concordance_ids))
    for record in concordance["records"]:
        assert record["status"] and record["caution"] and record["inventory_references"] is not None
        if record["djd_reference"] is not None:
            assert record.get("published_edition") or record.get("djd_basis"), f"DJD reference lacks supporting edition in {record['manuscript_id']}"
        line_map = record.get("transcription_line_map", [])
        line_keys = [(item.get("group"), item.get("digital_line")) for item in line_map]
        assert len(line_keys) == len(set(line_keys)), f"Duplicate digital line mapping in {record['manuscript_id']}"
        for item in line_map:
            assert item.get("group") and item.get("digital_line") is not None
            assert item.get("source_reference"), f"Missing line source in {record['manuscript_id']}"
            assert isinstance(item.get("passages", []), list)
        for passage in record["passage_coverage"]:
            assert isinstance(passage, dict), f"Passage coverage must be structured in {record['manuscript_id']}"
            assert passage["reference"] and passage["basis"] and passage["coverage_status"]
    fourq47 = next(r for r in concordance["records"] if r["manuscript_id"] == "4Q47 Josh a")
    extra_sources = fourq47.get("additional_transcription_sources", [])
    assert len(extra_sources) >= 1, "4Q47 later-fragment transcription source is missing"
    twty = next((item for item in extra_sources if "The Way to Yahuweh" in item.get("title", "")), None)
    assert twty and twty.get("license") == "CC BY-SA 4.0" and twty.get("url")
    groups = {item["fragment_group"] for item in twty.get("sections", [])}
    assert {"9 i–12", "9 ii, 13–16", "17–18", "19–22"}.issubset(groups)
    assert all(item.get("pdf_text_lines") and item.get("passage_refs") for item in twty["sections"])
    assert "kept separate" in twty.get("caution", "") or "separate" in twty.get("caution", "")
    assert len(dss["archive_browse_index"]["qumran_sites"]) >= 9
    print("Validated DSS metadata and passage concordance:", len(dss["records"]), len(concordance["records"]))

def validate_android():
    source = Path("app/src/main/java/org/scripturesofgod/archive/MainActivity.java").read_text(encoding="utf-8")
    for required in (
        "void openDssCatalogEntry(String item)", "void openDssConcordanceEntry(String item)",
        "DSS Passage Concordance", "openDssConcordanceEntry(item)", "openDssCatalogEntry(item)",
        "void searchCorpus(String query)", "void openBook(String name)", "ref.startsWith(bookName+\" \")", "boolean matchesExact(String text, String needle)", "matchesExact(body,needle)", "matchesExact(reference,needle)", "matchesExact(sourceReference,needle)", "passageRefs", "executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR)", "Search complete text corpus",
        "catalog/dss_passage_concordance.json", "transcription_text", "additional_transcription_sources", "PDF text layer",
        "Apocrypha and Deuterocanonical Writings", "Psalm 151", "Odes",
        "Prayer of Manasseh (Greek)", "2 Esdras / 4 Ezra (Latin)", "Prayer of Manasseh (Latin)",
        "source_reference", "apocrypha_coverage.json", "Source-file coverage audit", "Temple Scroll (11Q19)", "War Scroll (1QM)",
        "void translateVerse(String reference,String sourceText,String sourceLanguage)", "ClickableSpan", "translateVerse(selectedReference,selectedText,\"he\")", "additional_transcription_sources", "chooseTranslationLanguage()", "downloadModelIfNeeded", "TranslateLanguage.fromLanguageTag", "Tap to translate", "target_language"
    ):
        assert required in source, f"Android source is missing: {required}"
    names_match = re.search(r'String\[\] translationNames=\{([^}]+)\}', source)
    codes_match = re.search(r'String\[\] translationCodes=\{([^}]+)\}', source)
    assert names_match and codes_match, "Translation language selector is missing"
    names = re.findall(r'"([^"]+)"', names_match.group(1))
    codes = re.findall(r'"([^"]+)"', codes_match.group(1))
    assert len(names) == len(codes) == 59, "Expected all 59 ML Kit translation languages"
    assert len(set(codes)) == 59 and "tl" in codes, "Translation language codes are incomplete or duplicated"
    assert "com.google.mlkit.common.model.DownloadConditions" in source
    assert "Translation.getClient(options)" in source
    for book in REQUIRED_GREEK | REQUIRED_LATIN:
        assert f'"{book}"' in source, f"An imported Apocrypha book is missing from Android navigation: {book}"
    dss = json.loads((ROOT / "catalog/dead_sea_scrolls_register.json").read_text(encoding="utf-8"))
    ids = {r["id"] for r in dss["records"]}
    assert "11Q19" in ids and "1QM" in ids
    catalog = json.loads((ROOT / "catalog/source_catalog.json").read_text(encoding="utf-8"))
    datasets = {item["id"]: item for item in catalog["datasets"]}
    assert {"swete-lxx-apocrypha", "latin-library-apocrypha", "codex-sinaiticus-xml", "4q47-joshua-direct-transcription"}.issubset(datasets)
    assert "current complete 16-chapter import is a Latin transmission text" in " ".join(datasets["swete-lxx-apocrypha"]["limitations"])
    assert datasets["4q47-joshua-direct-transcription"]["license"] == "CC BY-SA 4.0"
    assert datasets["4q47-joshua-direct-transcription"]["source_url"]
    assert "2 Esdras / 4 Ezra" in " ".join(catalog["not_yet_integrated"])
    greek = json.loads((ROOT / "catalog/greek_manuscript_register.json").read_text(encoding="utf-8"))
    sinaiticus = next(r for r in greek["records"] if r["id"] == "Sinaiticus")
    digital = sinaiticus["digital_transcription_source"]
    assert digital["license"] == "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)"
    assert digital["source_url"] and digital["repository_url"] and digital["status"]
    assert "digital_transcription_source" in source
    print("Validated Android navigation, text search and manuscript source metadata")

sections = {"base": validate_base, "apocrypha": validate_apocrypha, "dss": validate_dss, "android": validate_android}
if len(sys.argv) != 2 or sys.argv[1] not in sections:
    raise SystemExit("Usage: python tools/validate_corpus.py base|apocrypha|dss|android")
sections[sys.argv[1]]()
