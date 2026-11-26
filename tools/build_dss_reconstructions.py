#!/usr/bin/env python3
"""Build verse-by-verse Hebrew readings using DSS words where they can be aligned safely.

The continuous base is the separately identified WLC witness. DSS tokens are
substituted only when their word-level passage alignment matches a high-confidence
ordered subsequence of that verse. Unmatched or too-fragmentary DSS readings remain
separate evidence; they are never guessed into the reading.
"""
import json
import pathlib
import re
import unicodedata
from collections import defaultdict

ASSETS = pathlib.Path("app/src/main/assets")
CORPUS = ASSETS / "corpus"
DSS_FILE = ASSETS / "dss" / "etcbc_transcriptions.jsonl"
BASE_FILE = CORPUS / "verses.jsonl"
OUT_FILE = CORPUS / "reconstructed_verses.jsonl"
INDEX_FILE = CORPUS / "reconstruction_index.json"

FINAL_FORMS = str.maketrans({"ך":"כ", "ם":"מ", "ן":"נ", "ף":"פ", "ץ":"צ"})
BOOK_NAMES = {
    "Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers","Deut":"Deuteronomy",
    "Josh":"Joshua","Judg":"Judges","Ruth":"Ruth","1Sam":"1 Samuel","2Sam":"2 Samuel",
    "1Kgs":"1 Kings","2Kgs":"2 Kings","1Chr":"1 Chronicles","2Chr":"2 Chronicles",
    "Ezra":"Ezra","Neh":"Nehemiah","Esth":"Esther","Job":"Job","Ps":"Psalms",
    "Prov":"Proverbs","Eccl":"Ecclesiastes","Song":"Song of Songs","Isa":"Isaiah",
    "Jer":"Jeremiah","Lam":"Lamentations","Ezek":"Ezekiel","Dan":"Daniel","Hos":"Hosea",
    "Joel":"Joel","Amos":"Amos","Obad":"Obadiah","Jonah":"Jonah","Mic":"Micah",
    "Nah":"Nahum","Hab":"Habakkuk","Zeph":"Zephaniah","Hag":"Haggai","Zech":"Zechariah","Mal":"Malachi"
}

def clean_token(value):
    value = unicodedata.normalize("NFD", str(value or ""))
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.translate(FINAL_FORMS)
    return re.sub(r"[^א-ת]", "", value)

def normalize_ref(value):
    value = re.sub(r"\s+", " ", str(value or "").strip())
    match = re.match(r"^([A-Za-z0-9]+)\.([0-9]+)\.([0-9]+)$", value)
    if match:
        return f"{match.group(1)} {match.group(2)}:{match.group(3)}"
    match = re.match(r"^([A-Za-z0-9]+)\s+([0-9]+)[:.]([0-9]+)$", value)
    if match:
        return f"{match.group(1)} {match.group(2)}:{match.group(3)}"
    return value

def lcs_pairs(base, witness):
    """Return ordered (base-index, witness-index) matches by normalized Hebrew form."""
    a = [clean_token(x) for x in base]
    b = [clean_token(x) for x in witness]
    rows, cols = len(a), len(b)
    dp = [[0] * (cols + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, -1, -1):
            if a[i] and a[i] == b[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    pairs, i, j = [], 0, 0
    while i < rows and j < cols:
        if a[i] and a[i] == b[j]:
            pairs.append((i, j)); i += 1; j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1
    return pairs

def parse_base_ref(record):
    ref = str(record.get("ref", "")).strip()
    match = re.match(r"^([A-Za-z0-9]+)\.([0-9]+)\.([0-9]+)$", ref)
    if match:
        return f"{match.group(1)} {match.group(2)}:{match.group(3)}"
    return normalize_ref(ref)

def main():
    if not BASE_FILE.exists() or not DSS_FILE.exists():
        raise SystemExit("Base corpus or imported DSS line corpus is missing.")
    dss_by_ref = defaultdict(lambda: defaultdict(list))
    line_counts = 0
    with DSS_FILE.open(encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line); line_counts += 1
            scroll = record.get("scroll", "unknown")
            fragment = record.get("fragment", "")
            line_no = record.get("line", "")
            for word in record.get("word_records", []):
                ref = normalize_ref(word.get("parallel_reference", ""))
                surface = str(word.get("surface", "")).strip()
                display = str(word.get("surface_full", "")).strip()
                if ref and surface and display:
                    dss_by_ref[ref][scroll].append({
                        "surface": surface, "display": display,
                        "coordinate": f"{scroll} {fragment}:{line_no}"
                    })

    counts = defaultdict(lambda: {"verses":0,"dss_aligned":0,"dss_fragment_only":0,"wlc_fallback":0})
    total = 0
    with BASE_FILE.open(encoding="utf-8") as source, OUT_FILE.open("w", encoding="utf-8", newline="\n") as target:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            # Only Hebrew WLC records are eligible for this Hebrew reconstruction layer.
            if record.get("language") != "he" or "Westminster Leningrad Codex" not in record.get("witness_basis", ""):
                target.write(json.dumps(record, ensure_ascii=False, separators=(",",":")) + "\n")
                continue
            ref = parse_base_ref(record)
            base_tokens = str(record.get("text", "")).split()
            book_code = ref.split(" ",1)[0] if " " in ref else "Unknown"
            book_name = BOOK_NAMES.get(book_code, book_code)
            stats = counts[book_code]; stats["verses"] += 1
            candidates = []
            for scroll, words in dss_by_ref.get(ref, {}).items():
                pairs = lcs_pairs(base_tokens, [w["surface"] for w in words])
                coverage = len(pairs) / max(1, len(base_tokens))
                if pairs:
                    candidates.append((coverage, len(pairs), scroll, words, pairs))
            candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
            output = list(base_tokens)
            note = ""
            witnesses = []
            if candidates:
                coverage, matched, scroll, words, pairs = candidates[0]
                coords = sorted({words[j]["coordinate"] for _,j in pairs})
                witnesses.append({"scroll":scroll,"matched_words":matched,"verse_word_coverage":round(coverage,3),"coordinates":coords})
                if coverage >= 0.70 and matched >= 3:
                    for i,j in pairs:
                        output[i] = words[j]["display"]
                    stats["dss_aligned"] += 1
                    note = (f"DSS witness {scroll} preserves {matched} word(s) aligned to this verse; "
                            f"the remaining word positions are supplied from the Westminster Leningrad Codex. "
                            f"This is a marked hybrid reading, not a complete DSS verse or a single ancient manuscript.")
                    record["source"] = "DSS + Westminster Leningrad Codex witness-led reconstruction"
                    record["edition"] = "Verse-level reconstruction; DSS tokens aligned to the WLC base"
                    record["witness_basis"] = f"{scroll} (aligned preserved words); Westminster Leningrad Codex (supplement for missing word positions)"
                    record["transcription_type"] = "hybrid reconstructed Hebrew reading"
                else:
                    stats["dss_fragment_only"] += 1
                    note = (f"DSS witness {scroll} has words mapped to this verse, but the surviving fragment does not "
                            f"meet the alignment threshold for a continuous reconstruction. The WLC supplies this verse; "
                            f"the DSS fragment remains separately available in the DSS transcription archive.")
                    record["source"] = "Westminster Leningrad Codex; DSS fragment cross-reference retained separately"
                    record["edition"] = "WLC verse with separate fragment-level DSS evidence"
                    record["witness_basis"] = "Westminster Leningrad Codex; fragmentary DSS evidence is not merged"
                    record["transcription_type"] = "continuous Hebrew witness text with DSS fragment note"
            else:
                stats["wlc_fallback"] += 1
                note = ("No word-level DSS alignment for this verse was found in the imported transcription dataset. "
                        "The Westminster Leningrad Codex supplies the continuous Hebrew text; this verse is not labelled DSS.")
                record["source"] = "Westminster Leningrad Codex"
                record["edition"] = "OSHB electronic transcription of the WLC base text"
                record["witness_basis"] = "Westminster Leningrad Codex; no DSS word-level alignment found in imported corpus"
                record["transcription_type"] = "Hebrew witness text"
            record["text"] = " ".join(output)
            record["reconstruction_note"] = note
            record["dss_witnesses"] = witnesses
            record["reconstruction_reference"] = ref
            record["reconstruction_method"] = "ordered exact-token alignment; DSS replaces only aligned word positions; WLC supplies unaligned positions"
            record["reconstruction_threshold"] = 0.70
            if candidates:
                record["license"] = "DSS transcription CC BY-NC 4.0; WLC base text public domain; OSHB annotations CC BY 4.0"
                record["attribution"] = (record.get("attribution","") +
                    "; DSS transcription attribution: Martin G. Abegg Jr.; ETCBC/CACCHT; Qumran Digital Reader, CC BY-NC 4.0.")
                record["dss_source_url"] = "https://github.com/evenderekh/QDR"
            else:
                record["license"] = "WLC base text is public domain; OSHB annotations CC BY 4.0"
            target.write(json.dumps(record, ensure_ascii=False, separators=(",",":")) + "\n")
            total += 1

    summary = {
        "schema_version":1,
        "record_type":"verse_level_dss_led_hebrew_reconstruction_index",
        "method":"Use word-level DSS tokens only when they align as an ordered subsequence of the WLC verse at >=70% verse-word coverage and at least three matched words. WLC supplies remaining word positions. Lower-coverage fragments are retained as separate evidence and the WLC verse remains the continuous reading.",
        "dss_source":"ETCBC/CACCHT Dead Sea Scrolls corpus, Martin Abegg transcriptions, structured QDR export",
        "dss_license":"CC BY-NC 4.0",
        "base_source":"Open Scriptures Hebrew Bible / Westminster Leningrad Codex",
        "base_license":"WLC public domain; OSHB annotations CC BY 4.0",
        "asset":"corpus/reconstructed_verses.jsonl",
        "dss_line_records_scanned":line_counts,
        "hebrew_verse_records":total,
        "books":{BOOK_NAMES.get(k,k):v for k,v in sorted(counts.items())},
        "limitations":[
            "This is a conservative digital word-alignment reconstruction, not a new diplomatic edition or a claim that a complete DSS manuscript survives.",
            "The WLC is a medieval Masoretic codex witness and is not described as the next-oldest physical manuscript.",
            "DSS fragments below the alignment threshold remain separate and are not guessed into the continuous reading.",
            "This first reconstruction layer covers the 39 Hebrew Scripture writings in the WLC source corpus. Apocryphal, versional, and lost writings require their own witness-specific reconstruction layers."
        ]
    }
    INDEX_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
    print(f"Built {total} Hebrew verse records from {line_counts} DSS line records.")
    for title, s in summary["books"].items():
        print(f"{title}: {s['verses']} verses; {s['dss_aligned']} hybrid; {s['dss_fragment_only']} fragment-only; {s['wlc_fallback']} WLC-only.")
    if total < 20000:
        raise SystemExit(f"Unexpectedly small Hebrew reconstruction corpus: {total} verses.")

if __name__ == "__main__":
    main()
