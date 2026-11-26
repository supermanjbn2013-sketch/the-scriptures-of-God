#!/usr/bin/env python3
"""Build a line-level evidence index from the curated DSS passage concordance.

This index preserves each source transcription line as a separate unit. Passage
references remain source-supplied comparison anchors; unassigned lines stay
unassigned. It does not reconstruct missing text or merge parallel witnesses.
"""
import json
from pathlib import Path

ASSETS = Path("app/src/main/assets")
CATALOG = ASSETS / "catalog"
OUT = ASSETS / "dss"
CONCORDANCE = CATALOG / "dss_passage_concordance.json"
WITNESSES = CATALOG / "manuscript_witness_register.json"
OUT.mkdir(parents=True, exist_ok=True)

concordance = json.loads(CONCORDANCE.read_text(encoding="utf-8"))
witness_register = json.loads(WITNESSES.read_text(encoding="utf-8"))
witness_by_shelfmark = {
    item.get("manuscript_id"): item
    for item in witness_register.get("records", [])
}
records = []
for manuscript in concordance.get("records", []):
    witness = witness_by_shelfmark.get(manuscript.get("manuscript_id"))
    if witness is None:
        raise ValueError(f"No manuscript witness register entry for {manuscript.get('manuscript_id')}")
    source = manuscript.get("transcription_source") or {}
    for line in manuscript.get("transcription_line_map", []):
        passages = list(line.get("passages") or [])
        text = str(line.get("transcription_text") or "")
        records.append({
            "id": f"{witness['id']}__{str(line['group']).replace(' ', '_')}__line_{line['digital_line']}",
            "writing_ids": witness["writing_ids"],
            "witness_id": witness["id"],
            "manuscript_id": manuscript["manuscript_id"],
            "language": manuscript.get("language"),
            "fragment_group": line["group"],
            "digital_line": line["digital_line"],
            "passage_references": passages,
            "passage_mapping_status": "source_explicitly_mapped" if passages else "source_unassigned",
            "transcription_text": text,
            "transcription_status": "transcription_present" if text.strip() else "line_reference_only_no_text_supplied",
            "source_reference": line["source_reference"],
            "editorial_note": line.get("note", ""),
            "transcription_source": source.get("title", "Curated manuscript concordance transcription"),
            "transcription_source_url": source.get("url", ""),
            "transcription_source_version": source.get("version", ""),
            "license": source.get("license", "See concordance source record"),
            "evidence_rule": "Transcription line preserved as displayed; passage references are source anchors, not proof of complete verse coverage. Unassigned lines remain unassigned."
        })

keys = [(r["witness_id"], r["fragment_group"], r["digital_line"]) for r in records]
if len(keys) != len(set(keys)):
    raise ValueError("Duplicate witness/fragment/line coordinates in DSS line evidence")
jsonl_path = OUT / "dss_passage_line_evidence.jsonl"
with jsonl_path.open("w", encoding="utf-8", newline="\n") as target:
    for record in records:
        target.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

summary = {
    "schema_version": 1,
    "record_type": "DSS line-level passage evidence index",
    "source_catalogue": "catalog/dss_passage_concordance.json",
    "witness_register": "catalog/manuscript_witness_register.json",
    "offline_asset": "dss/dss_passage_line_evidence.jsonl",
    "line_record_count": len(records),
    "explicitly_mapped_line_count": sum(r["passage_mapping_status"] == "source_explicitly_mapped" for r in records),
    "unassigned_line_count": sum(r["passage_mapping_status"] == "source_unassigned" for r in records),
    "witnesses": sorted({r["witness_id"] for r in records}),
    "policy": "Line-level source transcriptions are retained independently. No missing wording is supplied, and no line without a source passage anchor is assigned by inference."
}
(OUT / "dss_passage_line_evidence_index.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Indexed {len(records)} curated DSS transcription lines: {summary['explicitly_mapped_line_count']} with source passage anchors and {summary['unassigned_line_count']} unassigned.")
