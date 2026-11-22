#!/usr/bin/env python3
"""Fetch and normalize explicitly licensed Hebrew and Greek source texts.
No text is invented. Every generated record carries its source and licence.
"""
import json, pathlib, urllib.request, xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/corpus")
ROOT.mkdir(parents=True, exist_ok=True)
HEBREW = ["Gen","Exod","Lev","Num","Deut","Josh","Judg","Ruth","1Sam","2Sam","1Kgs","2Kgs","1Chr","2Chr","Ezra","Neh","Esth","Job","Ps","Prov","Eccl","Song","Isa","Jer","Lam","Ezek","Dan","Hos","Joel","Amos","Obad","Jonah","Mic","Nah","Hab","Zeph","Hag","Zech","Mal"]
GREEK = ["Matt","Mark","Luke","John","Acts","Rom","1Cor","2Cor","Gal","Eph","Phil","Col","1Thess","2Thess","1Tim","2Tim","Titus","Phlm","Heb","Jas","1Pet","2Pet","1John","2John","3John","Jude","Rev"]
NS = {"o":"http://www.bibletechnologies.net/2003/OSIS/namespace"}
def get(url):
    req=urllib.request.Request(url, headers={"User-Agent":"The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r: return r.read()
records=[]
for book in HEBREW:
    url=f"https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/{book}.xml"
    raw=get(url); root=ET.fromstring(raw)
    for verse in root.findall(".//o:verse", NS):
        ref=verse.attrib.get("osisID","")
        words=[]
        for child in list(verse):
            part="".join(child.itertext()).strip()
            if part: words.append(part)
        text=" ".join(words)
        if ref and text:
            records.append({"ref":ref,"language":"he","text":text,"source":"Open Scriptures Hebrew Bible / Westminster Leningrad Codex","source_url":url,"license":"CC BY 4.0","attribution":"Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb"})
for book in GREEK:
    url=f"https://raw.githubusercontent.com/Faithlife/SBLGNT/master/data/sblgnt/text/{book}.txt"
    raw=get(url).decode("utf-8-sig")
    for line in raw.splitlines():
        if "\t" not in line: continue
        ref,text=line.split("\t",1); ref=ref.strip(); text=text.strip()
        if ref and text and ref[0].isalpha() or (ref and ref[0].isdigit()):
            if any(ch.isdigit() for ch in ref):
                records.append({"ref":ref,"language":"grc","text":text,"source":"SBL Greek New Testament v1.2","source_url":url,"license":"CC BY 4.0","attribution":"SBL Greek New Testament, © 2010 Society of Biblical Literature and Logos Bible Software; CC BY 4.0. https://github.com/Faithlife/SBLGNT"})
out=ROOT/"verses.jsonl"
with out.open("w",encoding="utf-8") as f:
    for rec in records: f.write(json.dumps(rec,ensure_ascii=False)+"\n")
(ROOT/"SOURCE_NOTICES.txt").write_text(
"HEBREW: Open Scriptures Hebrew Bible, based on the Westminster Leningrad Codex. Text and morphology are separately attributed; CC BY 4.0 applies to OSHB project material.\n"
"Attribution: Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb\n\n"
"GREEK: SBL Greek New Testament v1.2. Copyright 2010 Society of Biblical Literature and Logos Bible Software. CC BY 4.0. https://github.com/Faithlife/SBLGNT\n\n"
"These are editions/transcriptions, not direct facsimile images of every ancient manuscript. They must not be labelled as DSS readings or as a complete critical apparatus.\n",encoding="utf-8")
print(f"Created {len(records)} verse records at {out}")
