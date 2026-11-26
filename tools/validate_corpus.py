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

WLC_EXPECTED_BOOK_CODES = {
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
    assert hebrew_codes == WLC_EXPECTED_BOOK_CODES, f"WLC base-witness coverage mismatch: missing={WLC_EXPECTED_BOOK_CODES - hebrew_codes}, unexpected={hebrew_codes - WLC_EXPECTED_BOOK_CODES}"
    assert greek_codes == GREEK_BOOK_CODES, f"SBLGNT book coverage mismatch: missing={GREEK_BOOK_CODES - greek_codes}, unexpected={greek_codes - GREEK_BOOK_CODES}"
    assert all(r.get("attribution") for r in hebrew + greek + latin)
    refs = [(r["language"], r["ref"]) for r in rows]
    assert len(refs) == len(set(refs)), "Duplicate verse references detected within a language"
    print(f"Validated {len(rows)} text records; WLC base witness {len(hebrew)} records across {len(hebrew_codes)} book divisions, Greek {len(greek)} across {len(greek_codes)} SBLGNT books, Latin {len(latin)}")

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
    enoch_witnesses = ("4Q201", "4Q202", "4Q204", "4Q205", "4Q206", "4Q207", "4Q208", "4Q209", "4Q210", "4Q211", "4Q212")
    jubilees_witnesses = ("4Q216", "4Q217", "4Q218", "4Q219", "4Q220", "4Q221", "4Q222", "4Q223_224", "4Q225")
    for witness in enoch_witnesses + jubilees_witnesses:
        assert witness in indexed_scrolls and indexed_scrolls[witness]["line_count"] > 0, f"Missing offline Qumran reference witness: {witness}"
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
        assert record["source_urls"]
        coverage = record.get("transcription_coverage")
        if coverage:
            key = "".join(ch.lower() for ch in coverage["scroll_identifier"] if ch.isalnum())
            assert key in {"".join(ch.lower() for ch in item["scroll"] if ch.isalnum()) for item in index["scrolls"]}
            indexed = next(item for item in index["scrolls"] if "".join(ch.lower() for ch in item["scroll"] if ch.isalnum()) == key)
            assert coverage["line_count"] == indexed["line_count"] > 0
            assert coverage["fragment_count"] == indexed["fragment_count"] > 0
            assert coverage["license"] == "CC BY-NC 4.0"
            assert coverage["offline_asset"] == "dss/etcbc_transcriptions.jsonl"
            assert "gaps" in coverage["coverage_note"]
            assert record["status"] == "offline transcription imported; line-level text available"
        else:
            assert record["status"] == "metadata catalogued; no matching line-level transcription in the imported dataset"
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


def validate_papyri():
    """Verify every imported papyrus index against its compressed page records."""
    catalog = json.loads((ROOT / "catalog/greek_manuscript_register.json").read_text(encoding="utf-8"))
    entries = {item["id"]: item for item in catalog["records"]}
    witnesses = {
        "P46": (10046, "p46", "papyrus_46_page_verse_transcription"),
        "P52": (10052, "p52", "papyrus_52_page_verse_transcription"),
        "P66": (10066, "p66", "papyrus_66_page_verse_transcription"),
        "P75": (10075, "p75", "papyrus_75_page_verse_transcription"),
        "P72": (10072, "p72", "papyrus_72_page_verse_transcription"),
        "P77": (10077, "p77", "papyrus_77_page_verse_transcription"),
    }
    for witness, (document_id, folder, record_type) in witnesses.items():
        entry = entries[witness]
        source = entry["digital_transcription_source"]
        assert source["document_id"] == document_id, f"{witness}: source document ID mismatch"
        assert source["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)", f"{witness}: unverified or changed licence"
        assert "integrated" in entry["status"].lower(), f"{witness}: register does not mark importer integrated"
        index_path = ROOT / f"papyri/{folder}/{folder}_index.json"
        assert index_path.exists(), f"{witness}: generated offline index missing"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        assert index["document_id"] == document_id and index["record_type"] == record_type
        assert index["license"] == source["license"] and index["source_url"] == source["source_url"]
        assert index["attribution"] and index["provider"] and index["scope_note"] and index["text_handling"]
        assert index["page_count"] == len(index["pages"]) > 0
        assert index["record_count"] >= 1 and index["text_record_count"] >= 1
        seen_pages = set()
        actual_records = 0
        actual_text_records = 0
        for page in index["pages"]:
            page_id = page["page_id"]
            assert page_id and page_id not in seen_pages, f"{witness}: duplicate or empty page ID"
            seen_pages.add(page_id)
            asset = ROOT / page["asset_file"]
            assert asset.exists() and asset.stat().st_size > 0, f"{witness}: missing compressed page {page_id}"
            page_records = 0
            with gzip.open(asset, "rt", encoding="utf-8") as stream:
                for raw in stream:
                    if not raw.strip():
                        continue
                    record = json.loads(raw)
                    assert record.get("page_id") == page_id
                    assert record.get("source_label") is not None
                    assert isinstance(record.get("column_ids"), list) and isinstance(record.get("line_ids"), list)
                    assert isinstance(record.get("correction_notes"), list)
                    assert record.get("text", "").strip(), f"{witness}: empty imported text record"
                    page_records += 1
                    actual_records += 1
                    actual_text_records += 1
            assert page_records == page["record_count"], f"{witness}: page record count mismatch for {page_id}"
        assert actual_records == index["record_count"], f"{witness}: index record count mismatch"
        assert actual_text_records == index["text_record_count"], f"{witness}: text record count mismatch"
        if witness == "P77":
            assert actual_records >= 5 and index["page_count"] >= 1, "P77 source output unexpectedly incomplete"
    print("Validated six papyrus witnesses against their generated offline page records.")

def validate_john():
    """Validate the verse-level manuscript index generated from imported witnesses."""
    path = ROOT / "catalog/john_witness_index.json"
    assert path.exists(), "John manuscript comparison index was not generated"
    index = json.loads(path.read_text(encoding="utf-8"))
    assert index["record_type"] == "john_verse_witness_index"
    assert index["book"] == "John" and index["verse_count"] == len(index["verses"])
    assert index["verse_count"] >= 860, f"John witness index unexpectedly small: {index['verse_count']}"
    assert "no record for a witness" in index["absence_policy"].lower()
    metadata = index["witness_metadata"]
    assert {"P52", "P66", "P75", "Vaticanus", "Sinaiticus"}.issubset(metadata)
    expected_minimums = {"P66": 700, "P75": 500, "Vaticanus": 850, "Sinaiticus": 850}
    for witness, minimum in expected_minimums.items():
        assert index["witness_verse_counts"][witness] >= minimum, f"{witness} verse index is incomplete"
        assert metadata[witness].get("source_url") and metadata[witness].get("license")
    refs = [item["reference"] for item in index["verses"]]
    assert len(refs) == len(set(refs)), "Duplicate John verse references in witness index"
    expected_starts = {f"John {chapter}:1" for chapter in range(1, 22) if chapter != 8}
    expected_starts.add("John 8:12")  # The pericope adulterae is absent from the early continuous witnesses.
    assert expected_starts.issubset(set(refs))
    for verse in index["verses"]:
        assert verse["reference"] == f"John {verse['chapter']}:{verse['verse']}"
        assert verse["witnesses"]
        for witness, record in verse["witnesses"].items():
            assert witness in metadata and record["text"].strip()
            assert record["pages"] or record["line_ids"], f"Missing source coordinates: {verse['reference']} / {witness}"
            assert isinstance(record["correction_notes"], list)
    assert "P66" in next(v for v in index["verses"] if v["reference"] == "John 1:1")["witnesses"]
    assert "P75" in next(v for v in index["verses"] if v["reference"] == "John 1:1")["witnesses"]
    assert "Vaticanus" in next(v for v in index["verses"] if v["reference"] == "John 17:11")["witnesses"]
    assert "Sinaiticus" in next(v for v in index["verses"] if v["reference"] == "John 21:25")["witnesses"]
    reading_path = ROOT / "catalog/unified_readings.json"
    assert reading_path.exists(), "Unified readings catalogue is missing"
    catalogue = json.loads(reading_path.read_text(encoding="utf-8"))
    john = next((item for item in catalogue["readings"] if item.get("writing_id") == "john"), None)
    assert john is not None, "John reading record is missing"
    segments = john["segments"]
    chapter_numbers = sorted(int(re.search(r"john-chapter-(\d+)$", item["segment_id"]).group(1)) for item in segments)
    assert chapter_numbers == list(range(1, 22)), f"John chapter sequence incomplete: {chapter_numbers}"
    assert john["coverage"]["completed_chapters"] == list(range(1, 22))
    assert john["coverage"]["remaining_chapters"] == []
    assert john["english_text"] == "\n\n".join(item["english_text"] for item in segments)
    assert all(item.get("source_witness_id") and item.get("source_location") and item.get("transcription_or_edition_basis") for item in segments)
    assert not re.search(r"\bLord Jesus\b", john["english_text"], re.IGNORECASE), "Do not insert 'Lord' into a translated verse where Greek κύριος is absent"
    assert "manuscript verification and textual audit remain incomplete" in john["coverage"]["completion_note"]
    print("Validated verse-level John manuscript index:", index["verse_count"], "verse references;", index["witness_verse_counts"])


def validate_android():
    source = Path("app/src/main/java/org/scripturesofgod/archive/MainActivity.java").read_text(encoding="utf-8")
    for required in (
        "void openDssCatalogEntry(String item)", "void openDssConcordanceEntry(String item)",
        "void openJohnWitnessComparison()", "void openJohnWitnessComparison(String initialReference)", "void showJohnWitnessVerse(int chapter,int verse)", "catalog/john_witness_index.json", "Compare a John passage", "john_witness_index.json",
        "DSS Passage Concordance", "DSS Transcription Archive", "void renderEtcbcDssIndex(String query)", "void openEtcbcDssScroll(String scrollId)", "dss/etcbc_transcriptions.jsonl", "dss/etcbc_scroll_index.json", "openDssConcordanceEntry(item)", "openDssCatalogEntry(item)",
        "void searchCorpus(String query)", "void openBook(String name)", "ref.startsWith(bookName+\" \")", "boolean matchesExact(String text, String needle)", "matchesExact(body,needle)", "matchesExact(reference,needle)", "matchesExact(sourceReference,needle)", "passageRefs", "executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR)", "Search complete text corpus",
        "catalog/dss_passage_concordance.json", "transcription_text", "additional_transcription_sources", "PDF text layer",
        "Apocrypha and Deuterocanonical Writings", "Psalm 151", "Odes",
        "Prayer of Manasseh (Greek)", "2 Esdras / 4 Ezra (Latin)", "Prayer of Manasseh (Latin)",
        "source_reference", "Temple Scroll (11Q19)", "War Scroll (1QM)",
        "Other Reference Books", "Protoevangelium of James (Nativity and Infancy of Jesus)", "Infancy Gospel of Thomas", "Gospel of Pseudo-Matthew", "Arabic Infancy Gospel", "Zohar", "Apocalypse of Moses", "Dormition of Mary (Transitus Mariae traditions)", "Six Books Dormition Apocryphon", "Book of Mary's Repose", "void openOtherReferenceBookEntry(String item)", "openOtherReferenceBookEntry(item)",
        "Translation connection settings · Target: ", "showTranslationSettings()", "Connect Gemini API key", "openAiConnectionSettings()", "openAiTranslator(String reference,String sourceText,String sourceLanguage)", "AI translate / analyze", "preferred_target_language", "Disciples and Apostles Writings", "Lost and Referenced Books", "openReferencedBookEntry(item)", "Book of the Wars of the LORD",
        "void showUnifiedWritingDetail(org.json.JSONObject record)", "showUnifiedWritingStudy(record);",
        'titleView.setOnClickListener(v->showUnifiedWritingDetail(record));',
        '.setPositiveButton("Read complete English text",(dialog,which)->showUnifiedEnglishReading(record))', "Book of Giants (fragmentarily preserved)", "void openBookOfGiantsFragments()", "4Q203", "4Q530", "4Q533", "openEtcbcDssScroll(ids.get(which))",
        "void openVaticanusArchive()", "void openVaticanusPage(String pageId)", "vaticanus/vaticanus_index.json",
        "void openPapyrus46Archive()", "void openPapyrus46Page(String pageId)", "papyri/p46/p46_index.json",
        "void openPapyrus52Archive()", "void openPapyrus52Page(String pageId)", "papyri/p52/p52_index.json",
        "void openPapyrus66Archive()", "void openPapyrus66Page(String pageId)", "papyri/p66/p66_index.json",
        "void openPapyrus75Archive()", "void openPapyrus75Page(String pageId)", "papyri/p75/p75_index.json",
        "void openPapyrus72Archive()", "void openPapyrus72Page(String pageId)", "papyri/p72/p72_index.json",
        "void openPapyrus77Archive()", "void openPapyrus77Page(String pageId)", "papyri/p77/p77_index.json", "Papyrus 77 (P77)",
        "void openDidacheArchive()", "void openDidacheChapter(int chapter)", "other_reference/didache/didache_index.json", "other_reference/didache/didache_greek.jsonl", "Open Greek text",
        "void openQumranReferenceFragments(String title,String[] requestedIds)", "4Q201", "4Q216", "4Q223_224", "Open Aramaic fragments", "Open Hebrew fragments",
        "void openHermasArchive()", "void openHermasBook(int book)", "other_reference/hermas/hermas_index.json", "other_reference/hermas/hermas_greek.jsonl",
        "void openThomasArchive()", "void openThomasPage(int page)", "other_reference/thomas/thomas_index.json", "other_reference/thomas/thomas_coptic.jsonl", "Open Coptic text",
        "void openGreekEnochArchive()", "void openGreekEnochPage(int page)", "other_reference/enoch_greek/enoch_greek_index.json", "other_reference/enoch_greek/enoch_greek.jsonl", "Open Greek fragments",
        "void openTestamentAbrahamArchive()", "void openTestamentAbrahamRecension(String recension)", "void openTestamentAbrahamChapter(String recension,int chapter,String assetFile)", "other_reference/testament_abraham/testament_abraham_index.json", "Open Greek recensions",
        "not a continuous reconstructed text or an English translation", "ClickableSpan", "openAiTranslator(selectedReference,selectedText,\"he\")", "additional_transcription_sources", "pdf_text_lines", "sourceTitle", "chooseTranslationLanguage()", "Tap to translate with Gemini AI", "showPassageActions(", "Bookmark passage", "Highlight passage", "Personal note", "archive_library", "font_size", "last_book", "target_language", "Back to ", "targetLanguage()"
    ):
        assert required in source, f"Android source is missing: {required}"
    for book in REQUIRED_GREEK | REQUIRED_LATIN:
        assert f'"{book}"' in source, f"An imported Apocrypha book is missing from Android navigation: {book}"

    historical_path = ROOT / "catalog/historical_writings_catalog.json"
    assert historical_path.exists(), "Historical writings catalogue is missing"
    historical = json.loads(historical_path.read_text(encoding="utf-8"))
    assert historical["record_type"] == "historical_writings_and_manuscript_witness_catalog"
    historical_records = historical["records"]
    historical_ids = [record["id"] for record in historical_records]
    historical_titles = {record["title"] for record in historical_records}
    assert len(historical_ids) == len(set(historical_ids)), "Duplicate historical-writing catalogue IDs"
    assert len(historical_records) >= 16, "Historical writings catalogue is unexpectedly incomplete"
    for record in historical_records:
        assert record["title"] and record["category"] and record["preservation"] and record["date"]
        assert isinstance(record["languages"], list) and isinstance(record["witnesses"], list)
        assert record["text_status"] and record["note"] and isinstance(record["sources"], list)
    required_historical = {
        "Book of the Wars of the Lord", "Book of Jashar", "Records of Samuel, Nathan, and Gad",
        "Paul's Earlier Letter to Corinth", "Paul's Severe / Sorrowful Letter to Corinth",
        "Letter Associated with Laodicea", "Prophecy / Book of Enoch (1 Enoch)",
        "Epistle of Barnabas", "Shepherd of Hermas", "1 Clement", "2 Clement", "Didache (Teaching of the Twelve Apostles)",
        "Gospel of Peter", "Gospel of Thomas", "Gospel of Mary", "Apocalypse of Peter"
    }
    assert required_historical.issubset(historical_titles), f"Missing historical writing records: {required_historical - historical_titles}"
    for required in (
        "Writings Mentioned in the Scriptures", "Early Disciple and Apostolic Writings",
        "Early Christian Gospels and Related Writings", "void openHistoricalWritingEntry(String title)",
        "catalog/historical_writings_catalog.json", "openHistoricalWritingEntry(item)"
    ):
        assert required in source, f"Historical writings Android navigation is missing: {required}"
    historical_json = json.dumps(historical)
    lost_catalog = json.loads((ROOT / "catalog/lost_and_referenced_books_catalog.json").read_text(encoding="utf-8"))
    assert lost_catalog["record_type"] == "lost_and_referenced_writings_catalog"
    lost_ids = [record["id"] for record in lost_catalog["records"]]
    assert len(lost_ids) == len(set(lost_ids)), "Duplicate lost-book record IDs"
    lost_titles = {record["title"] for record in lost_catalog["records"]}
    required_lost = {
        "Book of the Wars of the LORD", "Book of Jashar", "Acts of Solomon",
        "Chronicles of the Kings of Israel", "Chronicles of the Kings of Judah",
        "Records of Samuel, Nathan, and Gad", "Book of Laments for Josiah",
        "Chronicles of King David", "Samuel's Book of the Kingdom",
        "Records of Samuel the Seer", "Records of Nathan the Prophet",
        "Records of Gad the Seer", "Words or Records of the Kings of Israel",
        "Commentary (Midrash) on the Book of Kings",
        "Writings or Decrees of David and Solomon",
        "Book of the Kings of Israel (Chronicles source)",
        "Annals of the Kings of Israel (Manasseh source)",
        "Book of the Kings of Judah and Israel",
        "Book of the Kings of Israel and Judah",
        "Chronicles of the Levites",
        "Book of Giants (fragmentarily preserved)"
    }
    assert required_lost.issubset(lost_titles), f"Missing lost/referenced writing records: {required_lost - lost_titles}"
    assert "lost_and_referenced_books_catalog.json" in source
    assert "Book of Laments for Josiah" in source
    giants_record = next(record for record in lost_catalog["records"] if record["id"] == "book_giants")
    assert any("594 transcribed line records" in witness for witness in giants_record["witnesses"]), "Book of Giants fragment count and scope note is missing"
    assert "P.Oxy. 1782 (late 4th century Greek fragment)" in historical_json
    assert "P.Oxy. 3528" in historical_json and "not be casually assigned to Barnabas" in historical_json
    assert "must not automatically be identified as Paul's referenced letter" in historical_json

    manuscript_register = json.loads((ROOT / "catalog/greek_manuscript_register.json").read_text(encoding="utf-8"))
    p76 = next((record for record in manuscript_register["records"] if record.get("id") == "P76"), None)
    assert p76 is not None, "P76 individual manuscript catalogue record is missing"
    assert not p76.get("digital_transcription_source"), "Unauthorized P76 transcription source must not be bundled"
    assert not any("bham.ac.uk" in url or "iohannes.com" in url for url in p76.get("source_urls", [])), "Unauthorized transcription source URL remains in P76 record"
    assert "openP76Online" not in source and "downloadP76Transcription" not in source

    ai_source = Path("app/src/main/java/org/scripturesofgod/archive/AiTranslatorActivity.java").read_text(encoding="utf-8")
    for required in ("targetNames", "targetCodes", 'getSharedPreferences("archive_settings",MODE_PRIVATE).edit().putString("target_language",targetCodes[position]).apply()', "preferred_target_language"):
        assert required in ai_source, f"AI translation language preference is not synchronized: {required}"
    for required in ("Modern English translation", "Older English style (Early Modern)", "Literal translation", "Word-for-word analysis", "Grammar and meaning explanation", "gemini-3.1-flash-lite", "x-goog-api-key", "AndroidKeyStore", "AES/GCM/NoPadding", "aistudio.google.com/app/apikey", "do not invent words"):
        assert required in ai_source, f"AI translator is missing: {required}"
    assert "getAiKey()" not in source and "x-goog-api-key" not in source, "Main reader must not require a personal API key for translation"
    assert "translate.google.com" not in source and "com.google.mlkit" not in source, "Only Gemini AI translation is permitted in the reader"
    assert "open_connection_settings" in ai_source and "showKeyDialog()" in ai_source, "Gemini connection settings must be accessible from the main reader"
    manifest = Path("app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
    assert '.AiTranslatorActivity' in manifest and '.MainActivity' in manifest and 'android:exported="false"' in manifest, "AI translator screen must be registered as a private activity alongside the main Scripture reader"
    gradle = Path("app/build.gradle").read_text(encoding="utf-8")
    assert "versionCode 5" in gradle and "versionName '1.4.0'" in gradle and "com.google.mlkit:translate" not in gradle, "App version or obsolete translation dependency check failed"

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
    assert {"swete-lxx-apocrypha", "latin-library-apocrypha", "codex-sinaiticus-xml", "codex-vaticanus-ntvmr", "papyrus-46-ntvmr", "papyrus-52-ntvmr", "papyrus-66-ntvmr", "papyrus-75-ntvmr", "didache-first1k-greek", "shepherd-of-hermas-first1k-greek", "testament-abraham-first1k-greek", "gospel-thomas-coptic-scriptorium", "1-enoch-flemming-greek-fragments", "1-enoch-qumran-aramaic-fragments", "jubilees-qumran-hebrew-fragments", "4q47-joshua-direct-transcription", "etcbc-abegg-dss-transcriptions"}.issubset(datasets)
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
    p46 = next(r for r in greek["records"] if r["id"] == "P46")
    assert "integrated" in p46["status"].lower()
    assert p46["digital_transcription_source"]["document_id"] == 10046
    assert p46["digital_transcription_source"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert datasets["papyrus-46-ntvmr"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    p46_importer = Path("tools/import_papyrus_46.py").read_text(encoding="utf-8")
    assert "docID=10046" in p46_importer and "papyri/p46/pages/" in p46_importer
    p46_index_path = ROOT / "papyri/p46/p46_index.json"
    assert p46_index_path.exists(), "Offline Papyrus 46 index was not generated"
    p46_index = json.loads(p46_index_path.read_text(encoding="utf-8"))
    assert p46_index["document_id"] == 10046
    assert p46_index["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert p46_index["record_count"] >= 1000 and p46_index["text_record_count"] >= 1000
    assert p46_index["page_count"] == len(p46_index["pages"]) > 0
    p46_first = p46_index["pages"][0]
    p46_file = ROOT / p46_first["asset_file"]
    assert p46_file.exists() and p46_file.stat().st_size > 0
    with gzip.open(p46_file, "rt", encoding="utf-8") as page_stream:
        p46_sample = json.loads(next(page_stream))
    assert p46_sample.get("source_label") and p46_sample.get("text") and p46_sample.get("page_id")
    assert "correction_notes" in p46_sample
    p52 = next(r for r in greek["records"] if r["id"] == "P52")
    assert "integrated" in p52["status"].lower()
    assert p52["digital_transcription_source"]["document_id"] == 10052
    assert p52["digital_transcription_source"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert datasets["papyrus-52-ntvmr"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    p52_importer = Path("tools/import_papyrus_52.py").read_text(encoding="utf-8")
    assert "docID=10052" in p52_importer and "papyri/p52/pages/" in p52_importer
    p52_index_path = ROOT / "papyri/p52/p52_index.json"
    assert p52_index_path.exists(), "Offline Papyrus 52 index was not generated"
    p52_index = json.loads(p52_index_path.read_text(encoding="utf-8"))
    assert p52_index["document_id"] == 10052
    assert p52_index["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert p52_index["record_count"] >= 1 and p52_index["text_record_count"] >= 1
    assert p52_index["page_count"] == len(p52_index["pages"]) > 0
    p52_first = p52_index["pages"][0]
    p52_file = ROOT / p52_first["asset_file"]
    assert p52_file.exists() and p52_file.stat().st_size > 0
    with gzip.open(p52_file, "rt", encoding="utf-8") as page_stream:
        p52_sample = json.loads(next(page_stream))
    assert p52_sample.get("source_label") and p52_sample.get("text") and p52_sample.get("page_id")
    assert "correction_notes" in p52_sample
    p66 = next(r for r in greek["records"] if r["id"] == "P66")
    assert "integrated" in p66["status"].lower()
    assert p66["digital_transcription_source"]["document_id"] == 10066
    assert p66["digital_transcription_source"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert datasets["papyrus-66-ntvmr"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    p66_importer = Path("tools/import_papyrus_66.py").read_text(encoding="utf-8")
    assert "docID=10066" in p66_importer and "papyri/p66/pages/" in p66_importer
    p66_index_path = ROOT / "papyri/p66/p66_index.json"
    assert p66_index_path.exists(), "Offline Papyrus 66 index was not generated"
    p66_index = json.loads(p66_index_path.read_text(encoding="utf-8"))
    assert p66_index["document_id"] == 10066
    assert p66_index["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert p66_index["record_count"] >= 500 and p66_index["text_record_count"] >= 500
    assert p66_index["page_count"] == len(p66_index["pages"]) > 0
    p66_first = p66_index["pages"][0]
    p66_file = ROOT / p66_first["asset_file"]
    assert p66_file.exists() and p66_file.stat().st_size > 0
    with gzip.open(p66_file, "rt", encoding="utf-8") as page_stream:
        p66_sample = json.loads(next(page_stream))
    assert p66_sample.get("text") and p66_sample.get("page_id")
    assert "correction_notes" in p66_sample
    p75 = next(r for r in greek["records"] if r["id"] == "P75")
    assert "integrated" in p75["status"].lower()
    assert p75["digital_transcription_source"]["document_id"] == 10075
    assert p75["digital_transcription_source"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert datasets["papyrus-75-ntvmr"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    p75_importer = Path("tools/import_papyrus_75.py").read_text(encoding="utf-8")
    assert "docID=10075" in p75_importer and "papyri/p75/pages/" in p75_importer
    p75_index_path = ROOT / "papyri/p75/p75_index.json"
    assert p75_index_path.exists(), "Offline Papyrus 75 index was not generated"
    p75_index = json.loads(p75_index_path.read_text(encoding="utf-8"))
    assert p75_index["document_id"] == 10075
    assert p75_index["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert p75_index["record_count"] >= 1000 and p75_index["text_record_count"] >= 1000
    assert p75_index["page_count"] == len(p75_index["pages"]) > 0
    p75_first = p75_index["pages"][0]
    p75_file = ROOT / p75_first["asset_file"]
    assert p75_file.exists() and p75_file.stat().st_size > 0
    with gzip.open(p75_file, "rt", encoding="utf-8") as page_stream:
        p75_sample = json.loads(next(page_stream))
    assert p75_sample.get("text") and p75_sample.get("page_id")
    assert "correction_notes" in p75_sample
    p72 = next(r for r in greek["records"] if r["id"] == "P72")
    assert "integrated" in p72["status"].lower()
    assert p72["digital_transcription_source"]["document_id"] == 10072
    assert p72["digital_transcription_source"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert datasets["papyrus-72-ntvmr"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    p72_index_path = ROOT / "papyri/p72/p72_index.json"
    assert p72_index_path.exists(), "Offline Papyrus 72 index was not generated"
    p72_index = json.loads(p72_index_path.read_text(encoding="utf-8"))
    assert p72_index["document_id"] == 10072 and p72_index["page_count"] == len(p72_index["pages"]) > 0
    assert p72_index["record_count"] > 0 and p72_index["text_record_count"] > 0
    p77 = next(r for r in greek["records"] if r["id"] == "P77")
    assert "integrated" in p77["status"].lower()
    assert p77["digital_transcription_source"]["document_id"] == 10077
    assert p77["digital_transcription_source"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert datasets["papyrus-77-ntvmr"]["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    p77_importer = Path("tools/import_papyrus_77.py").read_text(encoding="utf-8")
    assert "docID=10077" in p77_importer and "papyri/p77/pages/" in p77_importer
    p77_index_path = ROOT / "papyri/p77/p77_index.json"
    assert p77_index_path.exists(), "Offline Papyrus 77 index was not generated"
    p77_index = json.loads(p77_index_path.read_text(encoding="utf-8"))
    assert p77_index["document_id"] == 10077
    assert p77_index["license"] == "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    assert p77_index["record_count"] >= 5 and p77_index["text_record_count"] >= 5
    assert p77_index["page_count"] == len(p77_index["pages"]) > 0
    p77_first = p77_index["pages"][0]
    p77_file = ROOT / p77_first["asset_file"]
    assert p77_file.exists() and p77_file.stat().st_size > 0
    with gzip.open(p77_file, "rt", encoding="utf-8") as page_stream:
        p77_sample = json.loads(next(page_stream))
    assert p77_sample.get("text") and p77_sample.get("page_id")
    assert "correction_notes" in p77_sample
    didache_path = ROOT / "other_reference/didache/didache_index.json"
    assert didache_path.exists(), "Offline Didache Greek index was not generated"
    didache_index = json.loads(didache_path.read_text(encoding="utf-8"))
    assert didache_index["chapter_count"] == 16 and didache_index["section_count"] >= 90
    assert didache_index["license"] == "CC BY-SA 4.0"
    assert didache_index["source_revision"] == "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
    assert datasets["didache-first1k-greek"]["license"] == "CC BY-SA 4.0"
    didache_records = [json.loads(line) for line in (ROOT / "other_reference/didache/didache_greek.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(didache_records) == didache_index["section_count"]
    assert {r["chapter"] for r in didache_records} == set(range(1, 17))
    assert all(r["language"] == "grc" and r["text"].strip() and r["reference"] and r["license"] == "CC BY-SA 4.0" for r in didache_records)
    assert all("printed" in r["textual_basis"].lower() for r in didache_records)
    hermas_path = ROOT / "other_reference/hermas/hermas_index.json"
    assert hermas_path.exists(), "Offline Shepherd of Hermas Greek index was not generated"
    hermas_index = json.loads(hermas_path.read_text(encoding="utf-8"))
    assert hermas_index["book_count"] == 27 and hermas_index["section_count"] >= 500
    assert hermas_index["license"] == "CC BY-SA 4.0"
    assert hermas_index["source_revision"] == "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
    assert datasets["shepherd-of-hermas-first1k-greek"]["license"] == "CC BY-SA 4.0"
    hermas_records = [json.loads(line) for line in (ROOT / "other_reference/hermas/hermas_greek.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(hermas_records) == hermas_index["section_count"]
    assert {r["book"] for r in hermas_records} == set(range(1, 28))
    assert all(r["language"] == "grc" and r["text"].strip() and r["reference"] and r["license"] == "CC BY-SA 4.0" for r in hermas_records)
    assert all("printed greek edition" in r["textual_basis"].lower() for r in hermas_records)
    abraham_path = ROOT / "other_reference/testament_abraham/testament_abraham_index.json"
    assert abraham_path.exists(), "Offline Testament of Abraham index was not generated"
    abraham_index = json.loads(abraham_path.read_text(encoding="utf-8"))
    assert abraham_index["license"] == "CC BY-SA 4.0"
    assert {r["recension"] for r in abraham_index["recensions"]} == {"A", "B"}
    assert datasets["testament-abraham-first1k-greek"]["license"] == "CC BY-SA 4.0"
    for recension in abraham_index["recensions"]:
        records = [json.loads(line) for line in (ROOT / recension["asset_file"]).read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(records) == recension["chapter_count"] >= 10
        assert {r["recension"] for r in records} == {recension["recension"]}
        assert {r["chapter"] for r in records} == set(recension["chapters"])
        assert all(r["language"] == "grc" and r["text"].strip() and r["reference"] and r["license"] == "CC BY-SA 4.0" for r in records)
        assert all("printed greek edition" in r["textual_basis"].lower() for r in records)
        assert all(isinstance(r["editorial_notes_and_variants"], list) for r in records)
    ignatius_path = ROOT / "other_reference/ignatius/ignatius_index.json"
    assert ignatius_path.exists(), "Offline Greek Ignatius index was not generated"
    ignatius_index = json.loads(ignatius_path.read_text(encoding="utf-8"))
    assert ignatius_index["source_revision"] == "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
    assert ignatius_index["license"] == "CC BY-SA 4.0" and ignatius_index["language_code"] == "grc"
    assert ignatius_index["letter_count"] == 7 and ignatius_index["section_count"] >= 150
    assert [item["number"] for item in ignatius_index["letters"]] == ["1","2","3","4","5","6","7"]
    ignatius_records = [json.loads(line) for line in (ROOT / "other_reference/ignatius/ignatius_greek.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(ignatius_records) == ignatius_index["section_count"]
    assert {r["letter"] for r in ignatius_records} == {"1","2","3","4","5","6","7"}
    assert all(r["language"] == "grc" and r["text"].strip() and r["license"] == "CC BY-SA 4.0" for r in ignatius_records)
    assert all(r["source_revision"] == ignatius_index["source_revision"] and isinstance(r["editorial_notes"], list) for r in ignatius_records)
    assert all("printed greek edition" in r["textual_basis"].lower() for r in ignatius_records)
    assert "void openIgnatiusArchive()" in source and "void openIgnatiusChapter(String letterNo,String chapter)" in source
    barnabas_path = ROOT / "other_reference/barnabas/barnabas_index.json"
    assert barnabas_path.exists(), "Offline Greek Barnabas index was not generated"
    barnabas_index = json.loads(barnabas_path.read_text(encoding="utf-8"))
    assert barnabas_index["source_revision"] == "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
    assert barnabas_index["license"] == "CC BY-SA 4.0" and barnabas_index["language_code"] == "grc"
    assert barnabas_index["chapter_count"] == 21 and barnabas_index["section_count"] == 194
    barnabas_records = [json.loads(line) for line in (ROOT / "other_reference/barnabas/barnabas_greek.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(barnabas_records) == 194
    assert {int(r["chapter"]) for r in barnabas_records} == set(range(1, 22))
    assert all(r["language"] == "grc" and r["text"].strip() and r["license"] == "CC BY-SA 4.0" for r in barnabas_records)
    assert all(r["source_revision"] == barnabas_index["source_revision"] and isinstance(r["editorial_notes"], list) and isinstance(r["cross_references"], list) for r in barnabas_records)
    assert all("printed greek edition" in r["textual_basis"].lower() for r in barnabas_records)
    assert "void openBarnabasArchive()" in source and "void openBarnabasChapter(String chapter)" in source
    assert datasets["epistle-barnabas-greek-lake-first1k"]["license"] == "CC BY-SA 4.0"
    thomas_path = ROOT / "other_reference/thomas/thomas_index.json"
    assert thomas_path.exists(), "Offline Gospel of Thomas Coptic index was not generated"
    thomas_index = json.loads(thomas_path.read_text(encoding="utf-8"))
    assert 17 <= thomas_index["page_count"] <= 20 and thomas_index["line_record_count"] >= 500
    assert thomas_index["pages"][0] == 32 and thomas_index["pages"][-1] == 51 and thomas_index["codex_page_range"] == [32, 51]
    assert thomas_index["license"] == "CC BY 4.0"
    assert thomas_index["source_revision"] == "e624efd798e3b49530472c7a4258db636222a826"
    assert datasets["gospel-thomas-coptic-scriptorium"]["license"] == "CC BY 4.0"
    thomas_records = [json.loads(line) for line in (ROOT / "other_reference/thomas/thomas_coptic.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(thomas_records) == thomas_index["line_record_count"]
    assert {int(r["page"]) for r in thomas_records} == set(thomas_index["pages"])
    assert len({r["saying"] for r in thomas_records}) >= 110
    assert all(r["language"] == "cop" and r["text"].strip() and r["line"] and r["license"] == "CC BY 4.0" for r in thomas_records)
    assert all("facsimile" in r["textual_basis"].lower() for r in thomas_records)
    ascension_path = ROOT / "other_reference/ascension_isaiah/ascension_isaiah_index.json"
    assert ascension_path.exists(), "Offline Ascension of Isaiah Ge'ez index was not generated"
    ascension_index = json.loads(ascension_path.read_text(encoding="utf-8"))
    assert ascension_index["source_revision"] == "671a29177071f19cc9da990aaad1681b338cdb49"
    assert ascension_index["record_count"] == 5 and ascension_index["section_count"] == 5
    assert "non-commercial" in ascension_index["license"].lower()
    assert datasets["ascension-isaiah-geez-beta-masaheft"]["license"].startswith("CC BY-SA 4.0")
    ascension_records = [json.loads(line) for line in (ROOT / "other_reference/ascension_isaiah/ascension_isaiah_geez.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(ascension_records) == ascension_index["record_count"]
    assert all(r["language"] == "gez" and r["text"].strip() and r["section"] and "non-commercial" in r["reuse_restriction"].lower() for r in ascension_records)
    assert all(r["source_revision"] == ascension_index["source_revision"] for r in ascension_records)
    assert "void openAscensionIsaiahArchive()" in source and "void openAscensionIsaiahSection(int section)" in source
    jubilees_geez_path = ROOT / "other_reference/jubilees_geez/jubilees_geez_index.json"
    assert jubilees_geez_path.exists(), "Offline Ge'ez Jubilees index was not generated"
    jubilees_geez_index = json.loads(jubilees_geez_path.read_text(encoding="utf-8"))
    assert jubilees_geez_index["source_revision"] == "ff9d4981eba2084c4914ca840ff323d85cbd2a1d"
    assert jubilees_geez_index["license"] == "CC BY-SA 4.0"
    assert len(jubilees_geez_index["editions"]) == 2
    assert all(e["chapter_count"] == 50 and e["record_count"] > 1000 for e in jubilees_geez_index["editions"])
    jubilees_geez_records = [json.loads(line) for line in (ROOT / "other_reference/jubilees_geez/jubilees_geez.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(jubilees_geez_records) == jubilees_geez_index["record_count"]
    assert {r["edition"] for r in jubilees_geez_records} == {"vanderkam_transcription", "eotc_printed"}
    assert all(r["language"] == "gez" and r["text"].strip() and r["license"] == "CC BY-SA 4.0" for r in jubilees_geez_records)
    assert "void openJubileesGeezArchive()" in source and "void openJubileesGeezChapter(String edition,int chapter)" in source
    twelve_patriarchs_path = ROOT / "other_reference/twelve_patriarchs/twelve_patriarchs_index.json"
    assert twelve_patriarchs_path.exists(), "Offline Greek Twelve Patriarchs index was not generated"
    twelve_patriarchs_index = json.loads(twelve_patriarchs_path.read_text(encoding="utf-8"))
    assert twelve_patriarchs_index["source_revision"] == "954a1f057c2426ad2f049b135600712812516242"
    assert twelve_patriarchs_index["license"] == "CC BY 4.0"
    assert twelve_patriarchs_index["language_code"] == "grc"
    assert twelve_patriarchs_index["testament_count"] == 12 and twelve_patriarchs_index["chapter_count"] >= 100 and twelve_patriarchs_index["record_count"] >= 900
    twelve_patriarchs_records = [json.loads(line) for line in (ROOT / "other_reference/twelve_patriarchs/twelve_patriarchs_greek.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(twelve_patriarchs_records) == twelve_patriarchs_index["record_count"]
    assert all(r["language"] == "grc" and r["text"].strip() and r["reading_witness"] == "Wikisource" for r in twelve_patriarchs_records)
    assert all("not yet collated against Charles" in r["textual_basis"] for r in twelve_patriarchs_records)
    assert "void openTwelvePatriarchsArchive()" in source and "openTwelvePatriarchsChapter(String testament,String chapter)" in source
    odes_path = ROOT / "other_reference/odes_of_solomon/odes_syriac_index.json"
    assert odes_path.exists(), "Offline Syriac Odes of Solomon index was not generated"
    odes_index = json.loads(odes_path.read_text(encoding="utf-8"))
    assert odes_index["source_revision"] == "833adc148cc356a6c70c16f81b22df9188df717a"
    assert odes_index["license"] == "CC BY 4.0"
    assert odes_index["language_code"] == "syr"
    assert odes_index["ode_count"] == 40 and odes_index["first_ode"] == 3 and odes_index["last_ode"] == 42
    assert odes_index["line_count"] >= 300 and odes_index["transcription_status"] == "UncorrectedTranscription"
    odes_records = [json.loads(line) for line in (ROOT / "other_reference/odes_of_solomon/odes_syriac.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(odes_records) == odes_index["line_count"]
    assert {r["ode"] for r in odes_records} == set(range(3, 43))
    assert all(r["language"] == "syr" and r["text"].strip() and r["source_revision"] == odes_index["source_revision"] for r in odes_records)
    assert "void openOdesOfSolomonArchive()" in source and "openOdesOfSolomonOde(String ode)" in source
    three_baruch_path = ROOT / "other_reference/3_baruch/3bar_greek_index.json"
    assert three_baruch_path.exists(), "Offline Greek 3 Baruch index was not generated"
    three_baruch_index = json.loads(three_baruch_path.read_text(encoding="utf-8"))
    assert three_baruch_index["source_revision"] == "954a1f057c2426ad2f049b135600712812516242"
    assert three_baruch_index["license"] == "CC BY 4.0"
    assert three_baruch_index["language_code"] == "grc"
    assert three_baruch_index["chapter_count"] >= 15 and three_baruch_index["record_count"] >= 100
    three_baruch_records = [json.loads(line) for line in (ROOT / "other_reference/3_baruch/3bar_greek.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(three_baruch_records) == three_baruch_index["record_count"]
    assert all(r["language"] == "grc" and r["text"].strip() and r["reading_witness"] == "Picard" for r in three_baruch_records)
    assert "void openThreeBaruchArchive()" in source and "openThreeBaruchChapter(String chapter)" in source
    baruch_path = ROOT / "other_reference/2_baruch/2_baruch_index.json"
    assert baruch_path.exists(), "Offline Syriac 2 Baruch index was not generated"
    baruch_index = json.loads(baruch_path.read_text(encoding="utf-8"))
    assert baruch_index["source_revision"] == "9850f5addade26f681334aa475570bef9b0b440a"
    assert baruch_index["license"] == "CC BY-NC 4.0"
    assert len(baruch_index["witnesses"]) == 3
    assert [w["witness"] for w in baruch_index["witnesses"]] == ["apocalypse", "epistle_a", "epistle_b"]
    baruch_records = [json.loads(line) for line in (ROOT / "other_reference/2_baruch/2_baruch_syriac.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(baruch_records) == baruch_index["record_count"] and len(baruch_records) > 700
    assert all(r["language"] == "syc" and r["text"].strip() and r["license"] == "CC BY-NC 4.0" for r in baruch_records)
    assert {r["witness"] for r in baruch_records} == {"apocalypse", "epistle_a", "epistle_b"}
    assert "void openTwoBaruchArchive()" in source and "openTwoBaruchChapter(String witness,int chapter)" in source or "openTwoBaruchChapter(String witness, int chapter)" in source
    enoch_greek_path = ROOT / "other_reference/enoch_greek/enoch_greek_index.json"
    assert enoch_greek_path.exists(), "Offline Greek 1 Enoch index was not generated"
    enoch_greek_index = json.loads(enoch_greek_path.read_text(encoding="utf-8"))
    assert enoch_greek_index["license"] == "CC BY-SA 4.0"
    assert enoch_greek_index["source_revision"] == "a1e7714108a71af5124e934038d06ba30003dc0c"
    assert enoch_greek_index["record_count"] >= 15 and enoch_greek_index["printed_pages"]
    assert enoch_greek_index["section_count"] > 0
    assert datasets["1-enoch-flemming-greek-fragments"]["license"] == "CC BY-SA 4.0"
    enoch_greek_records = [json.loads(line) for line in (ROOT / "other_reference/enoch_greek/enoch_greek.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(enoch_greek_records) == enoch_greek_index["record_count"]
    assert all(r["language"] == "grc" and r["text"].strip() and r["printed_page"] and r["chapter"] and r["section"] for r in enoch_greek_records)
    assert all(r["license"] == "CC BY-SA 4.0" and r["source_revision"] == enoch_greek_index["source_revision"] for r in enoch_greek_records)
    assert all("not a diplomatic transcription" in r["editorial_basis"].lower() for r in enoch_greek_records)
    print("Validated Android navigation, manuscript transcriptions, Didache, Shepherd of Hermas both Testament of Abraham recensions and the Coptic Gospel of Thomas and Greek 1 Enoch")


def validate_reconstruction_policy():
    path = ROOT / "catalog/text_reconstruction_policy.json"
    assert path.exists(), "Text reconstruction policy is missing"
    policy = json.loads(path.read_text(encoding="utf-8"))
    assert policy["record_type"] == "textual_reconstruction_policy"
    assert policy["archive_scope"] == "witness-led; no fixed canon or book-count limit"
    assert policy["primary_hebrew_reference"] == "Dead Sea Scrolls"
    assert len(policy["witness_traditions"]) >= 5
    ids = [item["id"] for item in policy["witness_traditions"]]
    assert len(ids) == len(set(ids)), "Duplicate witness-tradition IDs"
    for item in policy["witness_traditions"]:
        assert item["name"] and item["role"] and item["dating_note"] and item["handling_rule"]
    assert policy["reconstruction_rules"]["preserve_original_witnesses"] is True
    assert policy["reconstruction_rules"]["mark_every_supplement"] is True
    assert policy["reconstruction_rules"]["never_invent_missing_text"] is True
    assert policy["reconstruction_rules"]["unresolved_gaps_remain_blank"] is True
    assert policy["required_segment_fields"]
    wlc = next(item for item in source_catalog["datasets"] if item["id"] == "oshb-wlc")
    assert "Masoretic witness" in wlc["coverage"]
    assert "does not define the archive's scope" in " ".join(wlc["limitations"])
    print("Validated witness-led reconstruction policy and source provenance rules.")


def validate_witness_registers():
    catalog = json.loads((ROOT / "catalog/writing_catalog.json").read_text(encoding="utf-8"))
    witnesses = json.loads((ROOT / "catalog/manuscript_witness_register.json").read_text(encoding="utf-8"))
    coverage = json.loads((ROOT / "catalog/passage_coverage_map.json").read_text(encoding="utf-8"))
    assert catalog["record_type"] == "master_writing_catalog"
    assert witnesses["record_type"] == "manuscript_witness_register"
    assert coverage["record_type"] == "manuscript_passage_coverage_map"
    writing_ids = [x["id"] for x in catalog["records"]]
    witness_ids = [x["id"] for x in witnesses["records"]]
    coverage_ids = [x["id"] for x in coverage["records"]]
    assert len(writing_ids) == len(set(writing_ids)) and len(witness_ids) == len(set(witness_ids))
    assert len(coverage_ids) == len(set(coverage_ids))
    writing_set, witness_set = set(writing_ids), set(witness_ids)
    assert {"leviticus","numbers","deuteronomy","joshua","1_samuel","2_samuel"}.issubset(writing_set)
    for witness in witnesses["records"]:
        assert witness["writing_ids"] and set(witness["writing_ids"]).issubset(writing_set)
        assert witness["catalogue_record_id"] and witness["source_catalogue"]
    for item in coverage["records"]:
        assert item["writing_id"] in writing_set and item["witness_id"] in witness_set
        assert item["passage_reference"] and item["coverage_basis"]
        assert item["reconstruction_status"] == "not_reconstruction_ready"
        assert item["gap_fill_source_witness_id"] is None
    assert all(not x.get("text") for x in coverage["records"]), "Coverage inventory must not invent reconstructed text"
    traditions = json.loads((ROOT / "catalog/tradition_comparison_register.json").read_text(encoding="utf-8"))
    assert traditions["record_type"] == "textual_tradition_comparison_register"
    tradition_ids = [item["id"] for item in traditions["records"]]
    assert len(tradition_ids) == len(set(tradition_ids))
    for item in traditions["records"]:
        assert item["tradition"] in {"septuagint", "samaritan_pentateuch", "masoretic", "ethiopic"}
        assert item["writing_ids"] and set(item["writing_ids"]).issubset(writing_set)
        assert item["witness_or_collection"] and item["date_of_witness_or_tradition"]
        assert item["evidence_status"] and item["coverage_limitations"]
        assert item["passage_level_mapping_status"] in {"not_mapped", "partially_mapped"}
    assert {"septuagint", "samaritan_pentateuch", "masoretic", "ethiopic"}.issubset({x["tradition"] for x in traditions["records"]})
    print(f"Validated {len(traditions['records'])} comparison-tradition records; none is automatically reconstruction-ready.")
    print(f"Validated {len(catalog['records'])} writing identities, {len(witnesses['records'])} DSS witnesses, and {len(coverage['records'])} passage locators.")

    unified_path = ROOT / "catalog/unified_apostolic_disciple_writings.json"
    assert unified_path.exists(), "Unified apostolic and disciple writings catalogue is missing"
    unified = json.loads(unified_path.read_text(encoding="utf-8"))
    assert unified["record_type"] == "unified_apostolic_and_disciple_writings_catalog"
    unified_ids = [x["id"] for x in unified["records"]]
    assert len(unified_ids) == len(set(unified_ids)), "Duplicate unified writing identities"
    assert len(unified["records"]) > 27, "Unified collection must extend beyond the 27-item source dataset"
    assert unified["records"] == sorted(unified["records"], key=lambda r: (r.get("historical_sequence", 999), r.get("historical_subsequence", 999), r["title"].casefold())), "Unified writings are not sorted by historical event sequence"

    # Guard the event-based ordering against accidental reversion to composition-date order.
    assert all(isinstance(r.get("historical_sequence"), int) and isinstance(r.get("historical_subsequence"), int) for r in unified["records"])
    by_id = {r["id"]: r for r in unified["records"]}
    corinthian_order = [
        "paul_previous_corinthian_letter",
        "1_corinthians",
        "paul_sorrowful_corinthian_letter",
        "2_corinthians",
    ]
    corinthian_positions = [(by_id[x]["historical_sequence"], by_id[x]["historical_subsequence"]) for x in corinthian_order]
    assert corinthian_positions == sorted(corinthian_positions), "Corinthian correspondence must retain its qualified event sequence"
    assert "1 Corinthians 5:9" in by_id["paul_previous_corinthian_letter"]["historical_anchor_basis"], "The earlier Corinthian letter must retain its explicit textual reference"
    assert "2 Corinthians 2:1–4" in by_id["paul_sorrowful_corinthian_letter"]["historical_anchor_basis"] and "disputed" in by_id["paul_sorrowful_corinthian_letter"]["historical_anchor_basis"], "The painful letter must retain its internal references and disputed preservation"
    assert "literary unity of 2 Corinthians is disputed" in by_id["2_corinthians"]["historical_anchor_basis"], "Do not treat extant 2 Corinthians as an uncontested single dispatch"
    assert all(by_id[x].get("research_sources") for x in corinthian_order), "Corinthian correspondence chronology must include research sources"
    thessalonians = [by_id["1_thessalonians"], by_id["2_thessalonians"]]
    assert len({(r["historical_sequence"], r["historical_subsequence"]) for r in thessalonians}) == 1, "Do not force an exact order between the Thessalonian letters"
    assert "Timothy" in by_id["1_thessalonians"]["historical_anchor_basis"] and "Acts 17" in by_id["1_thessalonians"]["historical_anchor_basis"], "1 Thessalonians must retain its internal travel clues and qualified Acts correlation"
    assert "disputed" in by_id["2_thessalonians"]["historical_order_note"].lower(), "2 Thessalonians must retain its disputed relative order"
    assert "Romans 15:25" in by_id["romans"]["historical_anchor_basis"], "Romans must retain its Jerusalem-delivery journey anchor"
    pastoral_pair = [by_id["1_timothy"], by_id["titus"]]
    assert len({(r["historical_sequence"], r["historical_subsequence"]) for r in pastoral_pair}) == 1, "Do not force an exact order between 1 Timothy and Titus"
    assert all(term in by_id["1_timothy"]["historical_anchor_basis"] for term in ["1 Timothy 1:3", "Ephesus", "Macedonia", "3:14–15"]), "1 Timothy must retain its internal travel and stated-visit clues"
    assert all(term in by_id["titus"]["historical_anchor_basis"] for term in ["Titus 1:5", "Crete", "3:12", "Nicopolis", "3:13", "Dalmatia", "2 Timothy 4:10"]), "Titus must retain its internal itinerary clues and qualified Dalmatia connection"
    assert "not established" in by_id["titus"]["historical_anchor_basis"] and "unresolved" in by_id["titus"]["historical_order_note"], "Do not force Titus itinerary into an unproven sequence"
    revelation = by_id["revelation"]
    assert all(term in revelation["historical_anchor_basis"] for term in ["Revelation 1:4", "1:9", "1:11", "22:16", "Patmos", "seven assemblies"]), "Revelation must retain its internal Patmos and seven-assembly setting"
    assert "68–69 CE" in revelation["historical_anchor_basis"] and "Domitian" in revelation["historical_anchor_basis"], "Revelation must preserve the disputed early and late dating proposals"
    assert "does not identify John as the son of Zebedee" in revelation["historical_anchor_basis"], "Do not assume Revelation identifies its John as the apostle son of Zebedee"
    assert "does not establish an exact event-order relationship" in revelation["historical_order_note"], "Do not force Revelation into an exact chronology with other later writings"
    second_timothy = by_id["2_timothy"]
    assert all(term in second_timothy["historical_anchor_basis"] for term in ["Troas", "Carpus", "Miletus", "Trophimus", "Erastus", "4:16"]), "2 Timothy must retain its internal travel and hearing clues"
    assert "disputed" in second_timothy["historical_anchor_basis"].lower() and "Do not automatically place this after Acts" in second_timothy["historical_order_note"], "Do not force 2 Timothy into an unproven post-Acts chronology"
    peter = by_id["1_peter"]
    assert "1 Peter 1:1" in peter["historical_anchor_basis"] and "Silvanus" in peter["historical_anchor_basis"] and "Mark" in peter["historical_anchor_basis"], "1 Peter must retain its internal audience and closing-greeting clues"
    assert "commonly interpreted as Rome" in peter["historical_anchor_basis"] and "rather than an explicit place-name" in peter["historical_anchor_basis"], "Do not treat Babylon as an uncontested explicit place-name"
    assert "no exact relative event order" in peter["historical_order_note"], "Do not force 1 Peter into a precise relative chronology"
    ignatius_smyrna = {"ignatius_ephesians", "ignatius_magnesians", "ignatius_trallians", "ignatius_romans"}
    ignatius_troas = {"ignatius_philadelphians", "ignatius_smyrnaeans", "ignatius_polycarp"}
    assert all(by_id[x]["historical_subsequence"] == 120 for x in ignatius_smyrna), "Ignatius's Smyrna dispatches must share one event position"
    assert all(by_id[x]["historical_subsequence"] == 121 for x in ignatius_troas), "Ignatius's later Troas dispatches must share one event position"
    assert all(by_id[x]["historical_anchor_status"] == "journey_stage_internal_order_unresolved" for x in ignatius_smyrna | ignatius_troas), "Ignatius letters must preserve unresolved order within each journey stage"
    assert all("No exact order is claimed" in by_id[x]["historical_order_note"] for x in ignatius_smyrna | ignatius_troas), "Do not force a sequence among letters written at the same stop"
    for record in unified["records"]:
        start = record.get("composition_date_start_ce")
        end = record.get("composition_date_end_ce")
        assert (start is None) == (end is None), f"Date range must have two numeric values or two nulls: {record['id']}"
        assert start is None or (isinstance(start, int) and isinstance(end, int) and start <= end), f"Invalid composition date range: {record['id']}"
        assert start != 9999 and end != 9999, f"Do not use numeric sentinels for undated works: {record['id']}"
        assert record.get("attribution_status") and record.get("textual_status") and record.get("chronology_basis")
        assert isinstance(record.get("historical_sequence"), int) and record.get("historical_period") and record.get("historical_order_basis"), f"Missing event-based chronology metadata: {record['id']}"
        assert record.get("historical_anchor_id") and record.get("historical_anchor") and record.get("historical_anchor_basis") and record.get("historical_anchor_status"), f"Missing event-anchor evidence: {record['id']}"
        assert isinstance(record.get("historical_subsequence"), int), f"Missing event sub-sequence: {record['id']}"
        assert record.get("scope_relationship") in {"attributed_to_apostle_or_disciple", "attributed_to_or_associated_with_early_disciple", "anonymous_early_community_writing", "later_work_under_apostolic_or_disciple_name", "lost_or_reported_apostolic_correspondence", "broader_early_christian_context_association_unproven"}, f"Invalid scope relationship classification: {record['id']}"
        assert record.get("historical_order_note"), f"Missing relative-order qualification: {record['id']}"
        assert record.get("historical_anchor_status"), f"Missing event-anchor status: {record['id']}"
        if record.get("research_sources") is not None:
            assert record["research_sources"] and all(s.get("title") and s.get("url", "").startswith("https://") for s in record["research_sources"]), f"Invalid research source metadata: {record['id']}"
    print(f"Validated unified chronological writings collection: {len(unified['records'])} entries; not restricted to 27.")



sections = {"witnesses": validate_witness_registers, "reconstruction": validate_reconstruction_policy, "base": validate_base, "apocrypha": validate_apocrypha, "dss": validate_dss, "papyri": validate_papyri, "john": validate_john, "android": validate_android}
if len(sys.argv) != 2 or sys.argv[1] not in sections:
    raise SystemExit("Usage: python tools/validate_corpus.py witnesses|reconstruction|base|apocrypha|dss|papyri|john|android")
sections[sys.argv[1]]()
