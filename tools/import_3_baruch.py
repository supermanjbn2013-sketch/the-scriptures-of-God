#!/usr/bin/env python3
"""Import the Greek critical edition of 3 Baruch from the OCP TEI source."""
import json, pathlib, urllib.request, xml.etree.ElementTree as ET

ROOT=pathlib.Path("app/src/main/assets/other_reference/3_baruch")
REV="954a1f057c2426ad2f049b135600712812516242"
PATH="static/docs/tei/3Bar.xml"
URL=f"https://raw.githubusercontent.com/OnlineCriticalPseudepigrapha/Online-Critical-Pseudepigrapha/{REV}/{PATH}"
LICENSE="CC BY 4.0"
NS={"tei":"http://www.tei-c.org/ns/1.0"}

def text_content(node):
    return "".join(node.itertext()).strip()

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(URL,headers={"User-Agent":"The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(req,timeout=120) as response:data=response.read()
    (ROOT/"3bar_ocp_tei.xml").write_bytes(data)
    root=ET.fromstring(data)
    title=root.findtext(".//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title",namespaces=NS) or "3 Baruch"
    editors=[text_content(x) for x in root.findall(".//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:editor",NS)]
    source_bibl=[text_content(x) for x in root.findall(".//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:listWit/tei:witness[@xml:id='Picard']/tei:bibl",{"tei":NS,"xml":"http://www.w3.org/XML/1998/namespace"})]
    edition=root.find(".//tei:div[@type='edition'][@xml:id='ver_Greek']",{"tei":NS,"xml":"http://www.w3.org/XML/1998/namespace"})
    if edition is None:raise SystemExit("Greek edition div ver_Greek not found")
    records=[]; chapters=[]
    for chapter_node in edition.findall("./tei:div[@type='chapter']",NS):
        chapter=chapter_node.attrib.get("n","")
        chapters.append(chapter)
        for ab in chapter_node.findall("./tei:ab[@type='verse']",NS):
            verse=ab.attrib.get("n","")
            lemma=ab.find(".//tei:lem[@wit='#Picard']",NS)
            if lemma is None:continue
            value=text_content(lemma)
            if not value:continue
            records.append({"work":"3 Baruch","language":"grc","chapter":chapter,"verse":verse,"reference":f"3 Baruch {chapter}:{verse}","text":value,"reading_witness":"Picard","source_edition":"J.-C. Picard (ed.), Apocalypsis Baruchi Graece, PVTG 2 (Leiden: Brill, 1967), pp. 81–96","source_editor":"Online Critical Pseudepigrapha; TEI editors Ken M. Penner and David M. Miller","source_revision":REV,"source_url":URL,"license":LICENSE,"textual_basis":"Greek critical-edition lemma as encoded in OCP TEI; not a fresh diplomatic transcription of either surviving Greek manuscript. No unencoded variants are reconstructed."})
    if len(records)<100 or len(chapters)<15:raise SystemExit(f"Unexpected Greek coverage: {len(chapters)} chapters, {len(records)} records")
    with (ROOT/"3bar_greek.jsonl").open("w",encoding="utf-8",newline="\n") as out:
        for record in records:out.write(json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n")
    index={"schema_version":1,"work":title,"language":"Ancient Greek","language_code":"grc","source_repository":"Online Critical Pseudepigrapha","source_revision":REV,"source_url":URL,"license":LICENSE,"editors":editors,"base_text_witness":"Picard","source_bibliography":source_bibl,"chapters":chapters,"chapter_count":len(chapters),"record_count":len(records),"textual_basis":"Greek critical-edition lemma attributed to Picard (1967), represented in OCP's TEI edition. The OCP TEI header identifies Picard as the source for the Greek text and separately identifies the OCP translation witness. This is an edition-derived Greek text, not a fresh diplomatic transcription of either surviving Greek manuscript.","limitations":["Only the Greek critical-edition lemma is imported; the OCP translation and French translation divisions are not mixed into the Greek text.","The Slavonic tradition is not included or merged.","The source encodes the Greek lemma but no separate Greek variant readings in this TEI file; absence of encoded variants is not proof that manuscripts have no variants.","No missing wording is reconstructed."],"asset_file":"other_reference/3_baruch/3bar_greek.jsonl"}
    (ROOT/"3bar_greek_index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"SOURCE_NOTICE.txt").write_text("Online Critical Pseudepigrapha, 3 (Greek Apocalypse of) Baruch, TEI file static/docs/tei/3Bar.xml, revision "+REV+"\nGreek source text: J.-C. Picard (ed.), Apocalypsis Baruchi Graece (PVTG 2; Leiden: Brill, 1967), 81–96.\nTEI editors: Ken M. Penner and David M. Miller.\nLicense: CC BY 4.0. Attribute Online Critical Pseudepigrapha and the individual editors.\nEdition-derived text; not a fresh diplomatic transcription. Greek and Slavonic traditions remain separate.\n",encoding="utf-8")
    print(f"Imported 3 Baruch Greek critical edition: {len(chapters)} chapter/prologue divisions, {len(records)} numbered Greek text records (CC BY 4.0).")
if __name__=="__main__":main()
