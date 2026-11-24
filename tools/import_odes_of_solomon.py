#!/usr/bin/env python3
"""Import the Syriac Odes 3–42 from the Digital Syriac Corpus."""
import json,pathlib,urllib.request,xml.etree.ElementTree as ET
ROOT=pathlib.Path("app/src/main/assets/other_reference/odes_of_solomon")
REV="833adc148cc356a6c70c16f81b22df9188df717a"
BASE=f"https://raw.githubusercontent.com/srophe/syriac-corpus/{REV}/data/tei"
NS={"tei":"http://www.tei-c.org/ns/1.0"}
LICENSE="CC BY 4.0"
def text(node):return "".join(node.itertext()).strip()
def main():
    ROOT.mkdir(parents=True,exist_ok=True);odes=[];records=[]
    for corpus_id in range(146,186):
        url=f"{BASE}/{corpus_id}.xml"
        req=urllib.request.Request(url,headers={"User-Agent":"The-Scriptures-of-God-Archive/1.0"})
        with urllib.request.urlopen(req,timeout=90) as response:data=response.read()
        path=ROOT/f"{corpus_id}.xml";path.write_bytes(data)
        root=ET.fromstring(data)
        title_node=root.find(".//tei:title[@level='a']",NS)
        title=text(title_node) if title_node is not None else ""
        import re
        match=re.search(r"Ode\s+(\d+)",title)
        if not match:raise SystemExit(f"Cannot identify ode number in corpus item {corpus_id}: {title}")
        ode=int(match.group(1))
        body=root.find(".//tei:text/tei:body",NS)
        if body is None:raise SystemExit(f"No text body in corpus item {corpus_id}")
        stanzas=[]
        for stanza in body.findall(".//tei:lg[@type='stanza']",NS):
            n=stanza.attrib.get("n","")
            if not n:
                head=stanza.find("tei:head",NS);n=text(head) if head is not None else ""
            lines=[]
            for li,line in enumerate(stanza.findall("./tei:l",NS),1):
                value=text(line)
                if value:
                    lines.append(value)
                    records.append({"work":"Odes of Solomon","ode":ode,"stanza":n,"line":li,"reference":f"Ode {ode}, stanza {n}, line {li}","language":"syr","text":value,"source_corpus_id":corpus_id,"source_url":f"https://syriaccorpus.org/{corpus_id}","source_revision":REV,"license":LICENSE,"source_edition":"James H. Charlesworth (ed.), The Odes of Solomon: The Syriac Texts (Oxford: Oxford University Press, 1973).","transcriber":"Michael Oez","tei_encoder":"James E. Walters","textual_basis":"Digital Syriac Corpus print transcription based on Charlesworth (1973), explicitly marked UncorrectedTranscription. The Syriac base text is public domain; TEI encoding CC BY 4.0."})
            if lines:stanzas.append({"number":n,"line_count":len(lines)})
        if not stanzas:raise SystemExit(f"No Syriac stanza lines found for Ode {ode}")
        odes.append({"ode":ode,"title":f"Ode {ode}","corpus_id":corpus_id,"stanzas":stanzas,"stanza_count":len(stanzas),"line_count":sum(x["line_count"] for x in stanzas),"transcription_status":"UncorrectedTranscription"})
    odes.sort(key=lambda x:x["ode"])
    if len(odes)!=40 or [x["ode"] for x in odes]!=list(range(3,43)):raise SystemExit("Expected Odes 3–42 only; do not fill absent Odes 1–2.")
    if len(records)<300:raise SystemExit(f"Unexpectedly low Syriac line count: {len(records)}")
    with (ROOT/"odes_syriac.jsonl").open("w",encoding="utf-8",newline="\n") as out:
        for r in records:out.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
    index={"schema_version":1,"work":"Odes of Solomon","language":"Classical Syriac","language_code":"syr","source_repository":"Digital Syriac Corpus (Oxford-BYU Syriac Corpus)","source_revision":REV,"source_repository_url":f"https://github.com/srophe/syriac-corpus/tree/{REV}/data/tei","license":LICENSE,"base_text_status":"Public-domain Syriac base text; TEI XML edition CC BY 4.0.","source_edition":"James H. Charlesworth (ed.), The Odes of Solomon: The Syriac Texts (Oxford: Oxford University Press, 1973).","transcriber":"Michael Oez","tei_encoder":"James E. Walters","transcription_status":"UncorrectedTranscription (source TEI revisionDesc)","ode_count":len(odes),"first_ode":3,"last_ode":42,"stanza_count":sum(x["stanza_count"] for x in odes),"line_count":len(records),"odes":odes,"limitations":["This Syriac dataset contains Odes 3–42 only; Ode 2 is absent from the Syriac manuscript tradition represented by this source, and Ode 1 is not supplied by these files.","The source is a print transcription based on Charlesworth (1973), not a fresh diplomatic transcription of a manuscript image.","The source marks the transcription UncorrectedTranscription; possible transcription errors remain.","Greek and Coptic fragments and other manuscript witnesses are not merged into this Syriac text.","No missing wording is reconstructed."]}
    (ROOT/"odes_syriac_index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"SOURCE_NOTICE.txt").write_text("Digital Syriac Corpus, Odes of Solomon, corpus IDs 146–185, pinned repository revision "+REV+".\nBase text: James H. Charlesworth (ed.), The Odes of Solomon: The Syriac Texts (Oxford University Press, 1973). Syriac transcription: Michael Oez. TEI encoding: James E. Walters.\nLicense: Syriac base text public domain; TEI XML edition CC BY 4.0. Attribute the electronic edition and TEI encoder.\nThe source explicitly labels this a print transcription and UncorrectedTranscription. This archive contains Odes 3–42 only. Do not infer or reconstruct absent Odes 1–2; Greek and Coptic witnesses remain separate.\n",encoding="utf-8")
    print(f"Imported Odes 3–42: {len(odes)} odes, {sum(x['stanza_count'] for x in odes)} stanzas, {len(records)} Syriac lines.")
if __name__=="__main__":main()
