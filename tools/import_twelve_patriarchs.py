#!/usr/bin/env python3
"""Import the provisional Greek OCP base text for the Testaments of the Twelve Patriarchs."""
import json, pathlib, urllib.request, xml.etree.ElementTree as ET

ROOT=pathlib.Path("app/src/main/assets/other_reference/twelve_patriarchs")
REV="954a1f057c2426ad2f049b135600712812516242"
PATH="static/docs/tei/T12P.xml"
URL=f"https://raw.githubusercontent.com/OnlineCriticalPseudepigrapha/Online-Critical-Pseudepigrapha/{REV}/{PATH}"
NS={"tei":"http://www.tei-c.org/ns/1.0","xml":"http://www.w3.org/XML/1998/namespace"}
LICENSE="CC BY 4.0"

def content(node):
    return "".join(node.itertext()).strip()

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    request=urllib.request.Request(URL,headers={"User-Agent":"The-Scriptures-of-God-Archive/1.0"})
    with urllib.request.urlopen(request,timeout=120) as response:data=response.read()
    (ROOT/"twelve_patriarchs_ocp_tei.xml").write_bytes(data)
    root=ET.fromstring(data)
    edition=root.find(".//tei:div[@type='edition'][@xml:id='ver_Greek']",NS)
    if edition is None:raise SystemExit("Greek edition ver_Greek not found")
    witness=root.find(".//tei:listWit/tei:witness[@xml:id='Wikisource']",NS)
    witness_note=content(witness.find("tei:bibl",NS)) if witness is not None and witness.find("tei:bibl",NS) is not None else ""
    testament_index=[];records=[]
    for testament in edition.findall("./tei:div[@type='testament']",NS):
        name=testament.attrib.get("n","").strip()
        if not name:continue
        chapter_nodes=testament.findall("./tei:div[@type='chapter']",NS)
        chapter_numbers=[node.attrib.get("n","") for node in chapter_nodes]
        if not chapter_numbers:continue
        testament_index.append({"name":name,"label":"Testament of "+name,"chapters":chapter_numbers,"chapter_count":len(chapter_numbers)})
        for chapter_node in chapter_nodes:
            chapter=chapter_node.attrib.get("n","")
            for verse_node in chapter_node.findall("./tei:ab[@type='verse']",NS):
                verse=verse_node.attrib.get("n","")
                lemma=verse_node.find(".//tei:lem[@wit='#Wikisource']",NS)
                if lemma is None:continue
                text=content(lemma)
                if not text:continue
                records.append({"work":"Testaments of the Twelve Patriarchs","testament":name,"chapter":chapter,"verse":verse,"reference":f"Testament of {name} {chapter}:{verse}","language":"grc","text":text,"reading_witness":"Wikisource","source_revision":REV,"source_url":URL,"license":LICENSE,"source_edition":"OCP provisional Greek base text, apparently based on R. H. Charles (ed.), The Greek Versions of the Testaments of the Twelve Patriarchs (Oxford: Clarendon, 1908), but not yet collated against Charles.","source_editors":["Ken M. Penner","Ian W. Scott","David M. Miller"],"textual_basis":"Single Greek base-text witness encoded as Wikisource in the OCP TEI file. This is not a collated critical text or a fresh diplomatic transcription of a named ancient codex. The OCP TEI header explicitly labels the base text provisional and not yet collated against Charles."})
    testament_count=len(testament_index);chapter_count=sum(x["chapter_count"] for x in testament_index)
    if testament_count!=12 or chapter_count<100 or len(records)<900:raise SystemExit(f"Unexpected coverage: {testament_count} testaments, {chapter_count} chapters, {len(records)} verses")
    with (ROOT/"twelve_patriarchs_greek.jsonl").open("w",encoding="utf-8",newline="\n") as out:
        for record in records:out.write(json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n")
    index={"schema_version":1,"work":"Testaments of the Twelve Patriarchs","language":"Ancient Greek","language_code":"grc","source_repository":"Online Critical Pseudepigrapha","source_revision":REV,"source_url":URL,"license":LICENSE,"testaments":testament_index,"testament_count":testament_count,"chapter_count":chapter_count,"record_count":len(records),"base_text_witness":"Wikisource","witness_note":witness_note,"textual_basis":"Provisional single-witness Greek base text. OCP's TEI header says the text is Greek Wikisource, apparently the base text of R. H. Charles (1908), but not yet collated against Charles. Not a critical edition and not a fresh diplomatic transcription of a named ancient codex.","limitations":["Only the Greek base-text lemma is imported; no reconstructed variants are added.","The OCP TEI file identifies one base witness, Wikisource; it does not provide a multi-manuscript apparatus for this text.","The OCP source explicitly labels the base text provisional and not yet collated against Charles.","No missing wording is reconstructed."],"asset_file":"other_reference/twelve_patriarchs/twelve_patriarchs_greek.jsonl"}
    (ROOT/"twelve_patriarchs_index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"SOURCE_NOTICE.txt").write_text("Online Critical Pseudepigrapha, Testaments of the Twelve Patriarchs, TEI file static/docs/tei/T12P.xml, revision "+REV+"\nLicense: CC BY 4.0. TEI editors: Ken M. Penner, Ian W. Scott, David M. Miller.\nThe source header identifies the Greek Wikisource text as a provisional base, apparently related to R. H. Charles (1908), and explicitly says it has not yet been collated against Charles. It is not a critical edition or a diplomatic transcription of an identified ancient codex.\nKeep the Greek base text distinct from fragmentary Semitic-language evidence and all other versional traditions.\n",encoding="utf-8")
    print(f"Imported provisional Greek base text: {testament_count} testaments, {chapter_count} chapters, {len(records)} verse records (CC BY 4.0).")
if __name__=="__main__":main()
