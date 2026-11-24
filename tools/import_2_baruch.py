#!/usr/bin/env python3
"""Import Syriac 2 Baruch from the pinned ETCBC electronic Peshitta data."""
import json, pathlib, re, urllib.request

ROOT = pathlib.Path("app/src/main/assets/other_reference/2_baruch")
REV = "9850f5addade26f681334aa475570bef9b0b440a"
BASE = f"https://raw.githubusercontent.com/ETCBC/peshitta/{REV}/plain/0.2/"
LICENSE = "CC BY-NC 4.0"
CITATION = "Willem Th. van Peursen, Geert Jan Veldman, Constantijn Sikkel, Hannes Vlaardingerbroek and Dirk Roorda, ETCBC/peshitta (Version 0.3), 2018-10-17, https://doi.org/10.5281/zenodo.1464757"
FILES = [
    ("Apocalypse_of_Baruch.txt", "apocalypse", "Apocalypse of Baruch (2 Baruch 1–77)", 1, 77),
    ("Letter_of_Baruch_A.txt", "epistle_a", "Epistle of Baruch, Syriac text A (2 Baruch 78–86)", 78, 86),
    ("Letter_of_Baruch_B.txt", "epistle_b", "Epistle of Baruch, Syriac text B (2 Baruch 78–87)", 78, 87),
]

def fetch(name):
    req = urllib.request.Request(BASE + name, headers={"User-Agent": "The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read().decode("utf-8")

def parse(text, witness, title):
    records, chapter, verse, buf = [], None, None, []
    def flush():
        nonlocal buf, verse
        value = " ".join(" ".join(buf).split()).strip()
        if value and chapter is not None and verse is not None:
            records.append({
                "work": "2 Baruch", "witness": witness, "witness_title": title,
                "language": "syc", "chapter": chapter, "verse": verse,
                "reference": f"2 Baruch {chapter}:{verse}",
                "text": value, "textual_basis": "ETCBC electronic Peshitta text, derived by OCR from the printed Vetus Testamentum Syriace edition; main text only, without Brill critical apparatus.",
                "source_revision": REV, "license": LICENSE, "citation": CITATION
            })
        buf = []
    for raw in text.splitlines():
        line = raw.strip()
        m = re.fullmatch(r"Chapter\s+(\d+)", line)
        if m:
            flush(); chapter = int(m.group(1)); verse = None
            continue
        m = re.match(r"^(\d+)\s+(.*)$", line)
        if m and chapter is not None:
            flush(); verse = int(m.group(1)); buf = [m.group(2)]
        elif line and chapter is not None and verse is not None and not re.fullmatch(r"[•·܀\s]+", line):
            buf.append(line)
    flush()
    return records

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    all_records, groups = [], []
    for filename, witness, title, first, last in FILES:
        source = fetch(filename)
        (ROOT / filename).write_text(source, encoding="utf-8")
        records = parse(source, witness, title)
        chapters = sorted({r["chapter"] for r in records})
        if not records or chapters[0] != first or chapters[-1] != last:
            raise SystemExit(f"{filename}: unexpected coverage or no verse records")
        for record in records:
            record["source_file"] = filename
        all_records.extend(records)
        groups.append({"witness": witness, "title": title, "source_file": filename,
                       "chapters": chapters, "chapter_count": len(chapters),
                       "record_count": len(records)})
    with (ROOT / "2_baruch_syriac.jsonl").open("w", encoding="utf-8", newline="\n") as out:
        for record in all_records:
            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    index = {
        "schema_version": 1, "work": "2 Baruch", "language": "Classical Syriac",
        "language_code": "syc", "source_revision": REV, "source_repository": "ETCBC/peshitta",
        "source_url": f"https://github.com/ETCBC/peshitta/tree/{REV}/plain/0.2",
        "license": LICENSE, "citation": CITATION, "witnesses": groups,
        "record_count": len(all_records),
        "textual_basis": "Electronic Syriac Peshitta main text; source files were OCR-derived from the printed Vetus Testamentum Syriace edition. The critical apparatus is not included.",
        "limitations": [
            "The Syriac text is a translation from Greek; the Greek survives only in small fragments.",
            "The Apocalypse proper (chapters 1–77) and the two Syriac forms of the Epistle (A: 78–86; B: 78–87) are kept separate.",
            "The Epistle forms are not merged into one reconstructed text.",
            "This electronic text is OCR-derived from a printed edition and is not a fresh diplomatic transcription of Codex Ambrosianus.",
            "The source data is CC BY-NC 4.0; non-commercial use only. Commercial use requires permission from ETCBC or Brill.",
            "The printed edition's critical apparatus is not included."
        ],
        "asset_file": "other_reference/2_baruch/2_baruch_syriac.jsonl"
    }
    (ROOT / "2_baruch_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SOURCE_NOTICE.txt").write_text(CITATION + "\nLicence: CC BY-NC 4.0; non-commercial use only. Commercial use requires permission from ETCBC or Brill.\nTextual basis: OCR-derived electronic text of the Syriac Peshitta main text; critical apparatus omitted.\n", encoding="utf-8")
    print("Imported Syriac 2 Baruch:", ", ".join(f"{g['witness']} {g['chapter_count']} chapters/{g['record_count']} records" for g in groups), f"({len(all_records)} total records, CC BY-NC 4.0).")

if __name__ == "__main__":
    main()
