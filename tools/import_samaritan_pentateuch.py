#!/usr/bin/env python3
"""Import the CACCHT Samaritan Pentateuch as a separately identified Hebrew witness.

The source is the Text-Fabric dataset DT-UCPH/sp, version 7.4.1. Its text is
based on MS Dublin Chester Beatty Library 751 (Genesis 1:1–Deuteronomy 32:36)
and MS Garizim 1 (Deuteronomy 32:36b–34:10), as described by the source.
The import retains its scholarly transliteration; it is never converted into
Hebrew characters or silently merged into the WLC/DSS reading.
"""
import json
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path("app/src/main/assets")
OUT = ROOT / "corpus" / "samaritan_pentateuch.jsonl"
INDEX = ROOT / "corpus" / "samaritan_pentateuch_index.json"
SOURCE = pathlib.Path("build/samaritan-sp/tf/7.4.1")

BOOK_CODES = {
    "Genesis":"Gen", "Exodus":"Exod", "Leviticus":"Lev",
    "Numbers":"Num", "Deuteronomy":"Deut"
}
SOURCE_URL = "https://github.com/DT-UCPH/sp"
SOURCE_VERSION = "7.4.1"
SOURCE_COMMIT = "DT-UCPH/sp release directory tf/7.4.1"
MANUSCRIPTS = (
    "MS Dublin Chester Beatty Library 751 (Genesis 1:1–Deuteronomy 32:36); "
    "MS Garizim 1 (Deuteronomy 32:36b–34:10)"
)
ATTRIBUTION = (
    "Christian Canu Højgaard, Martijn Naaijer, and Stefan Schorch; "
    "CACCHT Samaritan Pentateuch Text-Fabric dataset, version 7.4.1"
)
LICENSE = "CC BY-NC 4.0"

def main():
    if not (SOURCE / "otype.tf").exists():
        raise SystemExit(f"Missing pinned Samaritan Pentateuch Text-Fabric data: {SOURCE}")
    try:
        from tf.fabric import Fabric
    except ImportError as exc:
        raise SystemExit("Install text-fabric before importing the Samaritan Pentateuch.") from exc

    api = Fabric(locations=str(SOURCE), silent="deep").load("book,chapter,verse,g_cons_raw")
    if api is None:
        raise SystemExit("Text-Fabric could not load the Samaritan Pentateuch features.")
    F, L = api.F, api.L
    grouped = defaultdict(list)
    for word in F.otype.s("word"):
        verses = L.u(word, otype="verse")
        if not verses:
            continue
        verse_node = verses[0]
        chapters = L.u(verse_node, otype="chapter")
        books = L.u(verse_node, otype="book")
        if not chapters or not books:
            continue
        book_name = F.book.v(books[0])
        code = BOOK_CODES.get(book_name)
        token = F.g_cons_raw.v(word)
        if not code or not token:
            continue
        chapter = F.chapter.v(chapters[0])
        verse = F.verse.v(verse_node)
        grouped[f"{code} {chapter}:{verse}"].append(str(token))

    records = []
    for ref, tokens in grouped.items():
        records.append({
            "ref": ref,
            "book_code": ref.split(" ", 1)[0],
            "language": "he-x-samaritan-transliteration",
            "text": " ".join(tokens),
            "source": "CACCHT Samaritan Pentateuch Text-Fabric dataset",
            "edition": f"DT-UCPH/sp Text-Fabric dataset v{SOURCE_VERSION}; g_cons_raw feature",
            "witness_basis": MANUSCRIPTS,
            "transcription_type": "Samaritan Hebrew consonantal scholarly transliteration",
            "source_url": SOURCE_URL,
            "source_version": SOURCE_VERSION,
            "source_revision": SOURCE_COMMIT,
            "license": LICENSE,
            "attribution": ATTRIBUTION,
            "text_status": "Separate Samaritan Pentateuch witness; not DSS, not WLC, and not converted into Hebrew script."
        })
    if len(records) < 5000:
        raise SystemExit(f"Unexpectedly low Samaritan Pentateuch coverage: {len(records)} verses")
    records.sort(key=lambda r: (r["book_code"], int(r["ref"].split()[1].split(":")[0]), int(r["ref"].split(":")[1])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as target:
        for record in records:
            target.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    summary = {
        "schema_version": 1,
        "record_type": "separate_samaritan_pentateuch_witness_index",
        "source": SOURCE_URL,
        "source_version": SOURCE_VERSION,
        "source_revision": SOURCE_COMMIT,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "manuscript_basis": MANUSCRIPTS,
        "feature": "g_cons_raw",
        "language_representation": "Samaritan Hebrew consonantal scholarly transliteration; not Hebrew Unicode script",
        "verse_record_count": len(records),
        "books": sorted({r["book_code"] for r in records}),
        "asset": "corpus/samaritan_pentateuch.jsonl",
        "limitations": [
            "The dataset is a scholarly transcription based on the manuscripts named above, not a new direct transcription from manuscript images.",
            "The transliteration is retained as supplied and is not transliterated back into Hebrew characters.",
            "Samaritan readings remain a separate witness and are not inserted into DSS or WLC text.",
            "The dataset license is non-commercial CC BY-NC 4.0."
        ]
    }
    INDEX.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(records)} Samaritan Pentateuch verse records across {len(summary['books'])} books.")

if __name__ == "__main__":
    main()
