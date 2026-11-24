#!/usr/bin/env python3
"""Validate generated text corpus, Apocrypha imports, DSS metadata, and Android navigation."""
import json
import sys
import gzip
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
    import json as json_module
    dss_lines_path = ROOT / "dss/etcbc_transcriptions.jsonl"
    dss_index_path = ROOT / "dss/etcbc_scroll_index.json"
    assert dss_lines_path.exists() and dss_index_path.exists(), "Offline ETCBC DSS transcription assets were not generated"
    index = json_module.loads(dss_index_path.read_text(encoding="utf-8"))
    assert index["license"] == "CC BY-NC 4.0" and index["total_line_records"] >= 10000
    indexed_scrolls = {item["scroll"]: item for item in index["scrolls"]}
    assert len(indexed_scrolls) >= 200, f"Unexpected DSS scroll coverage: {len(indexed_scrolls)}"
    required_witnesses = ("1QS", "1QM", "1QpHab", "1QH", "1QIsa")
    assert all(any(required.lower() in key.lower() for key in indexed_scrolls) for required in required_witnesses)
    actual_lines = 0
    found_major = set()
    with dss_lines_path.open(encoding="utf-8") as imported:
        for raw in imported:
            if not raw.strip():
                continue
            record = json_module.loads(raw)
            assert record.get("scroll") and record.get("fragment") and record.get("line")
            assert record.get("transcription_text") or record.get("normalized_text")
            assert record.get("license") == "CC BY-NC 4.0" and record.get("source_revision")
            assert record.get("attribution") and isinstance(record.get("parallel_references"), list)
            actual_lines += 1
            for required in required_witnesses:
                if required.lower() in record["scroll"].lower():
                    found_major.add(required)
    assert actual_lines == index["total_line_records"], f"DSS line count mismatch: {actual_lines}"
    assert found_major == set(required_witnesses), f"Major DSS witness missing from transcription lines: {set(required_witnesses)-found_major}"
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
        "DSS Passage Concordance", "DSS Transcription Archive", "void renderEtcbcDssIndex(String query)", "void openEtcbcDssScroll(String scrollId)", "dss/etcbc_transcriptions.jsonl", "dss/etcbc_scroll_index.json", "openDssConcordanceEntry(item)", "openDssCatalogEntry(item)",
        "void searchCorpus(String query)", "void openBook(String name)", "ref.startsWith(bookName+\" \")", "boolean matchesExact(String text, String needle)", "matchesExact(body,needle)", "matchesExact(reference,needle)", "matchesExact(sourceReference,needle)", "passageRefs", "executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR)", "Search complete text corpus",
        "catalog/dss_passage_concordance.json", "transcription_text", "additional_transcription_sources", "PDF text layer",
        "Apocrypha and Deuterocanonical Writings", "Psalm 151", "Odes",
        "Prayer of Manasseh (Greek)", "2 Esdras / 4 Ezra (Latin)", "Prayer of Manasseh (Latin)",
        "source_reference", "Temple Scroll (11Q19)", "War Scroll (1QM)",
        "Other Reference Books", "Protoevangelium of James (Nativity and Infancy of Jesus)", "Infancy Gospel of Thomas", "Gospel of Pseudo-Matthew", "Arabic Infancy Gospel", "Zohar", "Apocalypse of Moses", "Dormition of Mary (Transitus Mariae traditions)", "Six Books Dormition Apocryphon", "Book of Mary's Repose", "void openOtherReferenceBookEntry(String item)", "openOtherReferenceBookEntry(item)",
        "void translateVerse(String reference,String sourceText,String sourceLanguage)", "Disciples and Apostles Writings", "Lost and Referenced Books", "openReferencedBookEntry(item)", "Book of the Wars of YHWH", "Book of Giants (fragmentarily preserved)", "void openBookOfGiantsFragments()", "4Q203", "4Q530", "4Q533", "openEtcbcDssScroll(ids.get(which))",
        "void openVaticanusArchive()", "void openVaticanusPage(String pageId)", "vaticanus/vaticanus_index.json",
        "594 line records across these nine Qumran witness identifiers", "not a continuous reconstructed text or an English translation", "openGoogleTranslate(String sourceText,String targetLanguageCode)", "shareVerseForTranslation(String reference,String sourceText)", "ACTION_SEND", "translate.google.com", "ClickableSpan", "translateVerse(selectedReference,selectedText,\"he\")", "additional_transcription_sources", "pdf_text_lines", "sourceTitle", "chooseTranslationLanguage()", "Tap to translate  ·  Long press for passage tools", "showPassageActions(", "Bookmark passage", "Highlight passage", "Personal note", "archive_library", "font_size", "last_book", "target_language", "Back to ", "void translateOnDevice(", "com.google.mlkit.nl.translate.TranslatorOptions", "targetLanguage()"
    ):
        assert required in source, f"Android source is missing: {required}"
    for book in REQUIRED_GREEK | REQUIRED_LATIN:
        assert f'"{book}"' in source, f"An imported Apocrypha book is missing from Android navigation: {book}"

    ai_source = Path("app/src/main/java/org/scripturesofgod/archive/AiTranslatorActivity.java").read_text(encoding="utf-8")
    for required in ("Modern English translation", "Older English style (Early Modern)", "Literal translation", "Word-for-word analysis", "Grammar and meaning explanation", "gemini-3.1-flash-lite", "x-goog-api-key", "AndroidKeyStore", "AES/GCM/NoPadding", "aistudio.google.com/app/apikey", "do not invent words"):
        assert required in ai_source, f"AI translator is missing: {required}"
    assert "getAiKey()" not in source and "x-goog-api-key" not in source, "Main reader must not require a personal API key for translation"
    manifest = Path("app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
    assert '.AiTranslatorActivity' in manifest and '.MainActivity' in manifest and 'android:exported="false"' in manifest, "AI translator screen must be registered as a private activity alongside the main Scripture reader"
    gradle = Path("app/build.gradle").read_text(encoding="utf-8")
    assert "versionCode 5" in gradle and "versionName '1.4.0'" in gradle and "com.google.mlkit:translate" in gradle, "On-device translation app version or dependency is missing"

    mapping = re.search(r'String\[\]\[\] pairs=\{\{(.*?)\}\};', source, re.S)
    assert mapping, "Reader book-code mapping could not be inspected"
    book_pairs = re.findall(r'\{"([^"]+)","([^"]+)"\}', mapping.group(1))
    assert len(book_pairs) >= 60, f"Unexpected reader book mapping count: {len(book_pairs)}"
    for display_name, code in book_pairs:
        matches = [r for r in rows if r.get("book") == display_name or r.get("book_code") == code or r.get("ref", "").startswith(code + ".") or r.get("ref", "").startswith(code + " ") or r.get("ref", "").startswith(display_name + " ") or r.get("ref", "").startswith(display_name + ":")]
        assert matches, f"Book reader would show no records for {display_name} ({code})"
    for book in REQUIRED_GREEK | REQUIRED_LATIN:
        assert any(r.get("book") == book and r.get("text", "").strip() for r in rows), f"Reader has no text records for {book}"
    print(f"Validated reader record matching for {len(book_pairs)} standard books and {len(REQUIRED_GREEK | REQUIRED_LATIN)} Apocrypha forms")
    dss = json.loads((ROOT / "catalog/dead_sea_scrolls_register.json").read_text(encoding="utf-8"))
    ids = {r["id"] for r in dss["records"]}
    assert "11Q19" in ids and "1QM" in ids
    catalog = json.loads((ROOT / "catalog/source_catalog.json").read_text(encoding="utf-8"))
    datasets = {item["id"]: item for item in catalog["datasets"]}
    assert {"swete-lxx-apocrypha", "latin-library-apocrypha", "codex-sinaiticus-xml", "codex-vaticanus-ntvmr", "4q47-joshua-direct-transcription", "etcbc-abegg-dss-transcriptions"}.issubset(datasets)
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
    vaticanus = next(r for r in greek["records"] if r["id"] == "Vaticanus")
    assert "imported" in vaticanus["status"].lower()
    assert vaticanus["digital_transcription_source"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert datasets["codex-vaticanus-ntvmr"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    vaticanus_importer = Path("tools/import_codex_vaticanus.py").read_text(encoding="utf-8")
    assert "vaticanus/pages/" in vaticanus_importer and "pageID=ALL" in vaticanus_importer
    vaticanus_index_path = ROOT / "vaticanus/vaticanus_index.json"
    assert vaticanus_index_path.exists(), "Offline Codex Vaticanus index was not generated"
    vaticanus_index = json.loads(vaticanus_index_path.read_text(encoding="utf-8"))
    assert vaticanus_index["document_id"] == 20003
    assert vaticanus_index["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert vaticanus_index["record_count"] >= 1000 and vaticanus_index["text_record_count"] >= 1000
    assert vaticanus_index["page_count"] == len(vaticanus_index["pages"]) > 0
    first_page = vaticanus_index["pages"][0]
    page_file = ROOT / first_page["asset_file"]
    assert page_file.exists() and page_file.stat().st_size > 0
    with gzip.open(page_file, "rt", encoding="utf-8") as page_stream:
        sample_record = json.loads(next(page_stream))
    assert sample_record.get("source_label") and sample_record.get("text")
    assert "correction_notes" in sample_record and "page_id" in sample_record
    print("Validated Android navigation, text search, and Codex Vaticanus offline transcription")

sections = {"base": validate_base, "apocrypha": validate_apocrypha, "dss": validate_dss, "android": validate_android}
if len(sys.argv) != 2 or sys.argv[1] not in sections:
    raise SystemExit("Usage: python tools/validate_corpus.py base|apocrypha|dss|android")
sections[sys.argv[1]]()
