#!/usr/bin/env python3
"""Build a precise index of writings actually represented in imported DSS lines.

Only QDR parallel references or directly identified biblical manuscript
witnesses count as a biblical-book attestation. A title is never included
merely because it appears in a modern collection. Non-biblical compositions
are listed only when an explicitly mapped Qumran witness is present.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ASSETS = Path("app/src/main/assets")
DSS = ASSETS / "dss" / "etcbc_transcriptions.jsonl"
SCROLL_INDEX = ASSETS / "dss" / "etcbc_scroll_index.json"
OUT = ASSETS / "dss" / "dss_book_index.json"

BOOKS = {
    "Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers","Deut":"Deuteronomy",
    "Josh":"Joshua","Judg":"Judges","Ruth":"Ruth","1Sam":"1 Samuel","2Sam":"2 Samuel",
    "1Kgs":"1 Kings","2Kgs":"2 Kings","1Chr":"1 Chronicles","2Chr":"2 Chronicles",
    "Ezra":"Ezra","Neh":"Nehemiah","Esth":"Esther","Job":"Job","Ps":"Psalms",
    "Prov":"Proverbs","Eccl":"Ecclesiastes","Song":"Song of Songs","Isa":"Isaiah",
    "Jer":"Jeremiah","Lam":"Lamentations","Ezek":"Ezekiel","Dan":"Daniel","Hos":"Hosea",
    "Joel":"Joel","Amos":"Amos","Obad":"Obadiah","Jonah":"Jonah","Mic":"Micah",
    "Nah":"Nahum","Hab":"Habakkuk","Zeph":"Zephaniah","Hag":"Haggai","Zech":"Zechariah","Mal":"Malachi"
}
DIRECT_SCROLL_BOOKS = {
    "1qisaa":"Isa",       # Great Isaiah Scroll, 1QIsaᵃ
    "arugleviticus":"Lev",
    "xjoshua":"Josh",
    "xjudges":"Judg"
}

RELATED = [
    {"title":"1 Enoch","ids":["4Q201","4Q202","4Q204","4Q205","4Q206","4Q207","4Q208","4Q209","4Q210","4Q211","4Q212"],"language":"Aramaic"},
    {"title":"Jubilees","ids":["1Q17","1Q18","2Q19","3Q5","4Q216","4Q217","4Q218","4Q219","4Q220","4Q221","4Q222","4Q223_224","4Q225"],"language":"Hebrew"},
    {"title":"Book of Giants","ids":["1Q23","2Q26","4Q203","4Q530","4Q531","4Q532","4Q533","6Q8"],"language":"Aramaic"},
    {"title":"Tobit","ids":["4Q196","4Q197","4Q198","4Q199","4Q200"],"language":"Hebrew and Aramaic"},
    {"title":"Sirach","ids":["2Q18","11Q5"],"language":"Hebrew"},
    {"title":"Genesis Apocryphon","ids":["1Q20"],"language":"Aramaic"},
    {"title":"Prayer of Nabonidus","ids":["4Q242"],"language":"Aramaic"}
]

def norm_id(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())

def ref_code(value):
    value = str(value or "").strip()
    m = re.match(r"^([A-Za-z0-9]+)[. ]([0-9]+)[.:]([0-9]+)$", value)
    if not m:
        return None
    code = m.group(1)
    return code if code in BOOKS else None

def main():
    if not DSS.exists() or not SCROLL_INDEX.exists():
        raise SystemExit("DSS transcription or scroll index is missing.")
    stats = defaultdict(lambda: {"line_keys":set(), "references":set(), "scrolls":set(), "direct_scrolls":set(), "word_records":0})
    with DSS.open(encoding="utf-8") as source:
        for raw in source:
            if not raw.strip():
                continue
            row = json.loads(raw)
            scroll, fragment, line = row.get("scroll",""), row.get("fragment",""), row.get("line","")
            line_key = f"{scroll}|{fragment}|{line}"
            direct_code = DIRECT_SCROLL_BOOKS.get(norm_id(scroll))
            if direct_code:
                stats[direct_code]["line_keys"].add(line_key)
                stats[direct_code]["scrolls"].add(scroll)
                stats[direct_code]["direct_scrolls"].add(scroll)
            refs = set()
            for word in row.get("word_records", []):
                code = ref_code(word.get("parallel_reference"))
                if code:
                    refs.add(code)
            for ref in row.get("parallel_references", []):
                code = ref_code(ref)
                if code:
                    refs.add(code)
            for code in refs:
                item = stats[code]
                item["line_keys"].add(line_key)
                item["references"].update(
                    str(w.get("parallel_reference","")) for w in row.get("word_records",[])
                    if ref_code(w.get("parallel_reference")) == code
                )
                item["scrolls"].add(scroll)
                item["word_records"] += sum(1 for w in row.get("word_records",[]) if ref_code(w.get("parallel_reference")) == code)

    scroll_data = json.loads(SCROLL_INDEX.read_text(encoding="utf-8"))
    present = {norm_id(s.get("scroll")):s for s in scroll_data.get("scrolls",[])}
    books = []
    for code, title in BOOKS.items():
        item = stats.get(code)
        if not item:
            continue
        books.append({
            "book_code":code, "title":title, "language":"Hebrew",
            "preserved_line_count":len(item["line_keys"]),
            "parallel_reference_count":len(item["references"]),
            "word_record_count":item["word_records"],
            "witness_count":len(item["scrolls"]),
            "witnesses":sorted(item["scrolls"]),
            "direct_witnesses":sorted(item["direct_scrolls"]),
            "evidence_type":"Direct DSS manuscript identity plus QDR parallel-reference mapping" if item["direct_scrolls"] else "DSS line transcription with QDR parallel-reference mapping",
            "caution":"The parallel reference locates a textual parallel; it does not make the DSS line a complete verse or prove identical wording."
        })
    related = []
    for item in RELATED:
        witnesses = []
        for witness_id in item["ids"]:
            match = present.get(norm_id(witness_id))
            if match:
                witnesses.append({
                    "scroll":match["scroll"],
                    "fragment_count":match.get("fragment_count",0),
                    "line_count":match.get("line_count",0)
                })
        if witnesses:
            related.append({
                "title":item["title"], "language":item["language"],
                "witnesses":witnesses,
                "preserved_line_count":sum(w["line_count"] for w in witnesses),
                "evidence_type":"Imported Qumran manuscript transcription",
                "caution":"Only imported fragment and line records are displayed; this is not a complete copy of the work."
            })
    result = {
        "schema_version":1,
        "record_type":"DSS-attested writings index",
        "source":"ETCBC/CACCHT Dead Sea Scrolls transcriptions, Martin G. Abegg data distributed through Qumran Digital Reader",
        "source_revision":"f54f38464e18409eed8286fe24dd24f88d4735dd",
        "license":"CC BY-NC 4.0",
        "selection_rule":"A Hebrew Scripture book is listed when an imported DSS line has a QDR parallel reference to that book or a directly identified biblical manuscript witness is present. Additional writings are listed only when an explicitly identified witness is present in the imported scroll index.",
        "books":books,
        "related_writings":related,
        "scroll_identifier_count":len(scroll_data.get("scrolls",[])),
        "total_line_records":scroll_data.get("total_line_records",0),
        "limitations":[
            "QDR parallel references are concordance metadata, not manuscript wording and not proof that a complete verse survives.",
            "This index lists only works evidenced by the pinned imported transcription dataset; it is not a claim that no other Qumran fragments exist.",
            "A listed writing remains fragmentary wherever the manuscript evidence is fragmentary.",
            "Missing text is not filled in this index. Reconstruction is a separate layer and every supplied segment must name its source witness."
        ]
    }
    if not books:
        raise SystemExit("No biblical book references found in DSS import; refusing to publish an empty index.")
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Indexed {len(books)} Hebrew Scripture books with actual DSS manuscript evidence.")
    print(f"Indexed {len(related)} additional writings with explicitly matched DSS witness identifiers.")
    print(f"Included all {result['scroll_identifier_count']} imported scroll identifiers in the separate transcription archive.")

if __name__ == "__main__":
    main()
