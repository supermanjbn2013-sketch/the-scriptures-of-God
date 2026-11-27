#!/usr/bin/env python3
"""Preserve the reported Hebrew evidence from the medieval Ben Sira Rhyming Paraphrase.

The paraphrase is not a direct manuscript witness to Ben Sira's wording.
Only the short Sirach 23:1 phrase quoted by Jan Joosten's 2025 review is
transcribed here. Sirach 22:22-26 is recorded as a locator only.
"""
import json
import pathlib

ROOT = pathlib.Path("app/src/main/assets")
OUT = ROOT / "corpus/sirach/rhyming_paraphrase_evidence.jsonl"
INDEX = ROOT / "corpus/sirach/rhyming_paraphrase_evidence_index.json"
SOURCE_URL = "https://www.academia.edu/152613232/A_Critical_Edition_of_the_Hebrew_Manuscripts_of_Ben_Sira_With_Translations_and_Philological_Notes"
SOURCE_TITLE = (
    "Jan Joosten, Review of Frédérique Michèle Rey and Eric D. Reymond, "
    "A Critical Edition of the Hebrew Manuscripts of Ben Sira, "
    "Rivista Biblica 73 (2025), 576–581"
)

def main():
    rows = [
        {
            "writing_id": "sirach",
            "ref": "Sirach 23:1",
            "witness_id": "Rhyming-Paraphrase",
            "witness_type": "medieval_indirect_paraphrase_not_direct_Ben_Sira_manuscript",
            "manuscript_location": "ENA 3053.3 verso, line 1",
            "language": "Hebrew",
            "text": "אל אבי ואדון חיי",
            "text_status": "short_phrase_reported_in_secondary_scholarly_review; not a diplomatic transcription",
            "source_title": SOURCE_TITLE,
            "source_url": SOURCE_URL,
            "source_note": "The reviewer quotes this phrase as the Hebrew wording available for Sirach 23:1 in the Rhyming Paraphrase.",
            "gloss_reported_by_source": "God, my father, and master of my life",
            "reconstruction_use": "Indirect paraphrase evidence only. Do not substitute this wording for a direct Ben Sira manuscript reading or merge it into the reconstructed Hebrew text.",
            "license": "Short quotation from a copyrighted scholarly review; not a redistribution of the critical edition."
        },
        {
            "writing_id": "sirach",
            "ref": "Sirach 22:22-26",
            "witness_id": "Rhyming-Paraphrase",
            "witness_type": "medieval_indirect_paraphrase_not_direct_Ben_Sira_manuscript",
            "manuscript_location": "ENA 3053.3; exact side and line range require consultation of the critical edition",
            "language": "Hebrew",
            "text": None,
            "text_status": "passage_locator_only; no text copied",
            "source_title": SOURCE_TITLE,
            "source_url": SOURCE_URL,
            "source_note": "The review identifies a rhymed paraphrase of Sirach 22:22-26 in its discussion of the Adler manuscript ENA 3053.3.",
            "reconstruction_use": "Locator only. Do not infer the wording or use it to fill a gap until the manuscript and critical edition are checked.",
            "license": "Copyrighted scholarly edition; bibliographic locator only."
        }
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as target:
        for row in rows:
            target.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    INDEX.write_text(json.dumps({
        "schema_version": 1,
        "record_type": "sirach_indirect_rhyming_paraphrase_evidence",
        "record_count": len(rows),
        "text_record_count": sum(row["text"] is not None for row in rows),
        "locator_only_count": sum(row["text"] is None for row in rows),
        "source_title": SOURCE_TITLE,
        "source_url": SOURCE_URL,
        "limitations": [
            "The Rhyming Paraphrase is medieval and is not a direct Ben Sira manuscript.",
            "Its wording may paraphrase or reshape the source; it must never be silently merged into direct Hebrew witness text.",
            "Only a short phrase for Sirach 23:1 is quoted from the secondary review.",
            "Sirach 22:22-26 is a locator only; no Hebrew wording is supplied."
        ],
        "asset": "corpus/sirach/rhyming_paraphrase_evidence.jsonl"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Built 2 separate Rhyming Paraphrase evidence records: 1 quoted phrase and 1 locator only.")

if __name__ == "__main__":
    main()
