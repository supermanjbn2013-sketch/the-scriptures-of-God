#!/usr/bin/env python3
"""Import the two separately encoded Ge'ez Jubilees editions from Beta maṣāḥǝft."""
import json, pathlib, re, urllib.request, xml.etree.ElementTree as ET

ROOT = pathlib.Path("app/src/main/assets/other_reference/jubilees_geez")
REV = "ff9d4981eba2084c4914ca840ff323d85cbd2a1d"
PATH = "1001-2000/LIT1697Jubilees.xml"
URL = f"https://raw.githubusercontent.com/BetaMasaheft/Works/{REV}/{PATH}"
LICENSE = "CC BY-SA 4.0"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

def local(tag): return tag.rsplit("}", 1)[-1].lower()

def flatten(node):
    parts = []
    if node.text: parts.append(node.text)
    for child in list(node):
        tag = local(child.tag)
        if tag in ("lb", "pb", "cb"): parts.append(" ")
        elif tag == "gap": parts.append(" [lacuna] ")
        elif tag == "supplied": parts.append("[" + flatten(child) + "]")
        else: parts.append(flatten(child))
        if child.tail: parts.append(child.tail)
    return re.sub(r"\s+", " ", "".join(parts)).strip()

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent":"The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response: data = response.read()
    (ROOT / "LIT1697Jubilees.xml").write_bytes(data)
    root = ET.fromstring(data)
    editions = []
    for edition in root.iter():
        if local(edition.tag) != "div" or edition.attrib.get("type") != "edition" or edition.attrib.get(XML_LANG) != "gez": continue
        edition_id = edition.attrib.get("{http://www.w3.org/XML/1998/namespace}id", "")
        if edition_id == "Ran":
            edition_key, edition_title, basis = "vanderkam_transcription", "Ge'ez transcription of VanderKam's edition (Ran HaCohen)", "Transcription of James C. VanderKam's edition by Ran HaCohen, encoded by Beta maṣāḥǝft"
        elif edition_id == "EOTCed":
            edition_key, edition_title, basis = "eotc_printed", "Ethiopian Orthodox Tewahedo Church printed edition", "Standard printed EOTC edition, encoded by Beta maṣāḥǝft"
        else: continue
        records, chapters = [], set()
        for part in edition.iter():
            if local(part.tag) != "div" or part.attrib.get("type") != "textpart": continue
            subtype = part.attrib.get("subtype", "")
            if subtype not in ("chapter", "incipit"): continue
            chapter_raw = part.attrib.get("n", "")
            label_node = next((x for x in list(part) if local(x.tag) == "label"), None)
            label = flatten(label_node) if label_node is not None else ""
            if subtype == "chapter":
                try: chapter = int(chapter_raw)
                except ValueError: continue
                chapters.add(chapter)
            else: chapter = 0
            for ab in list(part):
                if local(ab.tag) != "ab": continue
                lines = [x for x in list(ab) if local(x.tag) == "l"]
                if lines:
                    for verse_node in lines:
                        verse = verse_node.attrib.get("n", "")
                        value = flatten(verse_node)
                        if value:
                            records.append({"work":"Jubilees","edition":edition_key,"edition_title":edition_title,"language":"gez","chapter":chapter,"verse":verse,"reference":("Jubilees introduction" if chapter == 0 else f"Jubilees {chapter}:{verse}"),"text":value,"edition_basis":basis,"source_revision":REV,"source_url":URL,"license":LICENSE})
                else:
                    value = flatten(ab)
                    if value:
                        records.append({"work":"Jubilees","edition":edition_key,"edition_title":edition_title,"language":"gez","chapter":chapter,"verse":"","reference":label or ("Jubilees introduction" if chapter == 0 else f"Jubilees {chapter}"),"text":value,"edition_basis":basis,"source_revision":REV,"source_url":URL,"license":LICENSE})
        if len(chapters) != 50 or len(records) < 1000:
            raise SystemExit(f"{edition_key}: unexpected coverage: {len(chapters)} chapters, {len(records)} records")
        editions.append({"edition":edition_key,"title":edition_title,"edition_basis":basis,"chapters":sorted(chapters),"chapter_count":len(chapters),"record_count":len(records),"records":records})
    if len(editions) != 2: raise SystemExit(f"Expected two Ge'ez editions, found {len(editions)}")
    records = [r for edition in editions for r in edition["records"]]
    with (ROOT/"jubilees_geez.jsonl").open("w",encoding="utf-8",newline="\n") as out:
        for r in records: out.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
    index={"schema_version":1,"work":"Jubilees","language":"Classical Ethiopic (Ge'ez)","language_code":"gez","source_repository":"Beta maṣāḥǝft / Works","source_revision":REV,"source_url":URL,"license":LICENSE,"editions":[{k:v for k,v in e.items() if k!="records"} for e in editions],"record_count":len(records),"textual_basis":"Two separate Ge'ez edition divisions in the pinned Beta maṣāḥǝft TEI file: a transcription of VanderKam's edition by Ran HaCohen and the standard printed EOTC edition. Neither is represented as a fresh diplomatic transcription of a named manuscript.","limitations":["The two Ge'ez editions are kept separate and are not conflated into a composite text.","These are edition-based texts, not fresh diplomatic transcriptions of individual codices.","The Qumran Hebrew fragments of Jubilees already held in the archive remain separate witnesses and are not merged with either Ge'ez edition.","No missing wording is reconstructed."],"asset_file":"other_reference/jubilees_geez/jubilees_geez.jsonl"}
    (ROOT/"jubilees_geez_index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"SOURCE_NOTICE.txt").write_text("Beta maṣāḥǝft, Works, LIT1697Jubilees.xml, pinned revision "+REV+"\nLicense: CC BY-SA 4.0\nThe TEI file contains a Ge'ez transcription of VanderKam's edition by Ran HaCohen and a separate standard printed EOTC edition. Both are kept separate.\n",encoding="utf-8")
    for e in editions: print(f"Imported {e['title']}: {e['chapter_count']} chapters, {e['record_count']} verse/section records.")
if __name__=="__main__": main()
