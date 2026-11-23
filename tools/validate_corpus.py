#!/usr/bin/env python3
"""Validate generated text corpus, Apocrypha imports, DSS metadata, and Android navigation."""
import json
import sys
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

def validate_base():
    assert len(rows) >= 30000, f"Unexpected corpus size: {len(rows)}"
    assert all(r.get("ref") and r.get("text") and r.get("source") for r in rows)
    assert any(r["language"] == "he" for r in rows)
    assert any(r["language"] == "grc" for r in rows)
    assert all(r.get("source_url") and r.get("transcription_type") for r in rows)
    refs = [(r["language"], r["ref"]) for r in rows]
    assert len(refs) == len(set(refs)), "Duplicate verse references detected within a language"
    print(f"Validated {len(rows)} text records; Hebrew {sum(r['language']=='he' for r in rows)}, Greek {sum(r['language']=='grc' for r in rows)}, Latin {sum(r['language']=='la' for r in rows)}")

def validate_apocrypha():
    records = [r for r in rows if r.get("book")]
    books = {r["book"] for r in records}
    assert REQUIRED_GREEK.issubset(books), f"Missing Greek books/forms: {REQUIRED_GREEK - books}"
    assert REQUIRED_LATIN.issubset(books), f"Missing Latin books: {REQUIRED_LATIN - books}"
    greek = [r for r in records if r["language"] == "grc"]
    latin = [r for r in records if r["language"] == "la"]
    assert all(r.get("license") == "CC BY-SA 4.0" and r.get("textual_form") for r in greek)
    assert all(r.get("license", "").startswith("Public Domain") and r.get("textual_form") for r in latin)
    assert all(r.get("source_url") and r.get("attribution") for r in records)
    assert all(r.get("source_reference") for r in greek), "A Greek Apocrypha record is missing its original source coordinate"
    for book in REQUIRED_GREEK | REQUIRED_LATIN:
        assert any(r["book"] == book and r["text"].strip() for r in records), f"Empty text: {book}"
    report = json.loads((ROOT / "corpus/apocrypha_import_report.json").read_text(encoding="utf-8"))
    assert (REQUIRED_GREEK | REQUIRED_LATIN).issubset(set(report)), "Apocrypha import report is incomplete"
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
    assert len(dss["archive_browse_index"]["qumran_sites"]) >= 9
    print("Validated DSS metadata and passage concordance:", len(dss["records"]), len(concordance["records"]))

def validate_android():
    source = Path("app/src/main/java/org/scripturesofgod/archive/MainActivity.java").read_text(encoding="utf-8")
    for required in (
        "void openDssCatalogEntry(String item)", "void openDssConcordanceEntry(String item)",
        "DSS Passage Concordance", "openDssConcordanceEntry(item)", "openDssCatalogEntry(item)",
        "void searchCorpus(String query)", "void openBook(String name)", "ref.startsWith(bookName+\" \")", "boolean matchesExact(String text, String needle)", "matchesExact(body,needle)", "executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR)", "Search complete text corpus",
        "catalog/dss_passage_concordance.json", "transcription_text",
        "Apocrypha and Deuterocanonical Writings", "Psalm 151", "Odes",
        "Prayer of Manasseh (Greek)", "2 Esdras / 4 Ezra (Latin)", "Prayer of Manasseh (Latin)",
        "source_reference", "Temple Scroll (11Q19)", "War Scroll (1QM)"
    ):
        assert required in source, f"Android source is missing: {required}"
    for book in REQUIRED_GREEK | REQUIRED_LATIN:
        assert f'"{book}"' in source, f"An imported Apocrypha book is missing from Android navigation: {book}"
    dss = json.loads((ROOT / "catalog/dead_sea_scrolls_register.json").read_text(encoding="utf-8"))
    ids = {r["id"] for r in dss["records"]}
    assert "11Q19" in ids and "1QM" in ids
    print("Validated Android navigation and text search")

sections = {"base": validate_base, "apocrypha": validate_apocrypha, "dss": validate_dss, "android": validate_android}
if len(sys.argv) != 2 or sys.argv[1] not in sections:
    raise SystemExit("Usage: python tools/validate_corpus.py base|apocrypha|dss|android")
sections[sys.argv[1]]()
