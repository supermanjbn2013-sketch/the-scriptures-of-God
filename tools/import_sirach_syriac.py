#!/usr/bin/env python3
"""Import the Syriac Peshitta text of Ben Sira as a separate versional witness.

Source: ETCBC Syriac Corpus 0.92, pinned to commit 0b6ded2b. The underlying
text is the preliminary Ben Sira text from Vetus Testamentum Syriace (Peshitta
Institute/Brill), without its critical apparatus. It is a Syriac translation
witness, not a Hebrew manuscript and not a Hebrew retroversion.
"""
import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path("app/src/main/assets")
SOURCE = pathlib.Path("build/syriac/tf/0.92")
OUT = ROOT / "corpus/sirach/peshitta_syriac.jsonl"
INDEX = ROOT / "corpus/sirach/peshitta_syriac_index.json"
SOURCE_URL = "https://github.com/ETCBC/syriac"
SOURCE_REVISION = "0b6ded2b369c7d81589a98c92325290e24b20af6"
LICENSE = "CC BY-NC 4.0"
ATTRIBUTION = (
    "ETCBC Syriac Corpus 0.92, Eep Talstra Centre for Bible and Computer "
    "(Vrije Universiteit Amsterdam) with CACCHT; compiled by Martijn Naaijer; "
    "contributors credited in the upstream repository. Base text: Vetus "
    "Testamentum Syriace, Peshitta Institute (Brill), preliminary Ben Sira text."
)


def main():
    if not (SOURCE / "otype.tf").exists():
        raise SystemExit(f"Missing pinned ETCBC Syriac Text-Fabric source: {SOURCE}")
    try:
        from tf.fabric import Fabric
    except ImportError as exc:
        raise SystemExit("Install text-fabric before importing the Syriac Peshitta.") from exc

    api = Fabric(locations=str(SOURCE), silent="deep").load("book,chapter,verse,g_cons_utf8")
    if api is None:
        raise SystemExit("Text-Fabric could not load the Syriac Peshitta features.")
    F, L = api.F, api.L
    grouped = defaultdict(list)
    for word in F.otype.s("word"):
        verses = L.u(word, otype="verse")
        if not verses:
            continue
        verse_node = verses[0]
        chapters = L.u(verse_node, otype="chapter")
        books = L.u(verse_node, otype="book")
        if not chapters or not books or F.book.v(books[0]) != "Sir":
            continue
        token = F.g_cons_utf8.v(word)
        if not token:
            continue
        chapter = F.chapter.v(chapters[0])
        verse = F.verse.v(verse_node)
        grouped[(int(chapter), int(verse))].append(str(token))

    records = []
    for (chapter, verse), tokens in sorted(grouped.items()):
        records.append({
            "writing_id": "sirach",
            "ref": f"Sirach {chapter}:{verse}",
            "chapter": chapter,
            "verse": verse,
            "language": "syc",
            "text": " ".join(tokens),
            "source": "ETCBC Syriac Corpus 0.92",
            "edition": "Vetus Testamentum Syriace, Peshitta Institute (Brill), preliminary Ben Sira text; no critical apparatus",
            "witness_basis": "Syriac Peshitta textual tradition",
            "transcription_type": "Syriac versional text in Estrangela Unicode",
            "source_url": SOURCE_URL,
            "source_revision": SOURCE_REVISION,
            "license": LICENSE,
            "attribution": ATTRIBUTION,
            "text_status": "separate_ancient_versional_witness_not_Hebrew_manuscript",
            "reconstruction_use": "Compare same passage with Greek and surviving Hebrew witnesses; do not translate back into Hebrew without marking the result as editorial retroversion."
        })
    if len(records) < 500:
        raise SystemExit(f"Unexpectedly low Syriac Sirach coverage: {len(records)} verses")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\\n") as target:
        for record in records:
            target.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\\n")
    INDEX.write_text(json.dumps({
        "schema_version": 1,
        "record_type": "sirach_syrian_peshitta_version_index",
        "writing_id": "sirach",
        "source": SOURCE_URL,
        "source_revision": SOURCE_REVISION,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "edition": "Vetus Testamentum Syriace, Peshitta Institute (Brill), preliminary Ben Sira text; no critical apparatus",
        "verse_record_count": len(records),
        "chapter_count": len({r["chapter"] for r in records}),
        "chapters": sorted({r["chapter"] for r in records}),
        "asset": "corpus/sirach/peshitta_syriac.jsonl",
        "limitations": [
            "This is the Syriac Peshitta version, not a direct Hebrew manuscript.",
            "The upstream Ben Sira text is preliminary and has no critical apparatus.",
            "The Peshitta is an ancient versional witness; it must be compared passage by passage with Greek and Hebrew witnesses.",
            "The source is CC BY-NC 4.0 and is restricted to non-commercial use."
        ]
    }, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Imported {len(records)} Syriac Peshitta Sirach verses across {len({r['chapter'] for r in records})} chapters.")


if __name__ == "__main__":
    main()
