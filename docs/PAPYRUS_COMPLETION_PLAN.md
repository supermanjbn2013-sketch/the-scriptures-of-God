# Papyrus Archive Completion Plan

Updated: 2026-11-24

## Verified repository state

The following importer scripts are present in the default branch and are wired into `.github/workflows/validate-corpus.yml`:

| Witness | Importer | Current integration |
|---|---|---|
| P46 | `tools/import_papyrus_46.py` | NTVMR TEI import during corpus validation/build |
| P52 | `tools/import_papyrus_52.py` | NTVMR TEI import during corpus validation/build |
| P66 | `tools/import_papyrus_66.py` | NTVMR TEI import during corpus validation/build |
| P75 | `tools/import_papyrus_75.py` | NTVMR TEI import during corpus validation/build |
| P72 | `tools/import_papyrus_72.py` | NTVMR TEI import during corpus validation/build |
| P77 | `tools/import_papyrus_77.py` | NTVMR TEI import during corpus validation/build |

P76 has a manuscript-register entry and a publicly listed IGNTP TEI XML file, but there is no `tools/import_papyrus_76.py` in the current repository. Do not label P76 as imported or complete until its exact XML header, reuse terms, TEI structure, and transcription output have been checked.

## Immediate work order

1. **P76** — inspect the complete IGNTP XML header and file encoding; establish the exact applicable licence and attribution; parse its TEI structure; preserve original readings, supplied text, uncertainty, corrections, and source coordinates; add a reproducible importer only after these checks.
2. **P77** — validate generated page/record counts against the NTVMR source and inspect page, column, line, supplied-reading, and correction handling. Do not infer missing text.
3. **P72** — validate the composite-codex coverage and ensure each work/fragment remains distinguished in the page index and reader.
4. **P46, P52, P66, P75** — run source-to-output checks and verify the app opens each offline page index correctly.
5. **Expand coverage** — inventory additional papyri with accessible, reusable institutional transcriptions. Do not assume every listed witness has a downloadable transcription or compatible licence.
6. **Only after papyrus work is complete** — resume Codex Sinaiticus work.

## Further John papyri to investigate

A 2011 notice describing IGNTP releases lists these additional witnesses with John transcriptions: P2, P5, P6, P22, P28, P36, P39, P44A, P44B, P45, P55, P59, P60, P63, P80, P84, P90, P93, P95, P106, P107, P108, and P109. This is a discovery list, not proof that every file remains accessible or that its historical licence still applies. Each witness requires a fresh repository and licence check before import.

## Source and reuse controls

- INTF NTVMR transcription endpoint for P72: https://ntvmr.uni-muenster.de/community/api/transcript/get/?docID=10072&pageID=ALL&format=teiraw
- INTF NTVMR transcription endpoint for P77: https://ntvmr.uni-muenster.de/community/api/transcript/get/?docID=10077&pageID=ALL&format=teiraw
- IGNTP P76 repository item: https://epapers.bham.ac.uk/id/eprint/1760/
- IGNTP P76 XML file: https://epapers.bham.ac.uk/id/eprint/1760/6/04_P76.xml
- IGNTP XML transcription guidelines (version 1.6; states CC BY 4.0 for the guidelines document itself): https://epapers.bham.ac.uk/id/eprint/4301/5/IGNTP_XML_guidelines_1-6.pdf
- Historical notice listing the John papyri transcriptions and their then-stated CC BY-NC-SA terms: https://e-homoreligiosus.blogspot.com/2011/08/igntp-papyrus-transcriptions-released.html

The licence of a guideline document is not automatically the licence of an individual transcription. The P76 file's own header and repository record must control. Do not copy, bundle, or redistribute a transcription until its individual reuse terms are verified.

## Completion criteria

A witness is complete only when all of the following are true:

- A primary institutional source and exact transcription version are recorded.
- The file's applicable licence and required attribution are verified.
- The importer is reproducible and rejects malformed or unexpectedly incomplete downloads.
- Source-attested page, column, line, verse/section labels, corrections, supplied readings, and uncertainty are preserved where encoded.
- Missing physical text is not reconstructed from another edition.
- Generated offline index and compressed records pass structural and source-count checks.
- The Android reader opens the witness and displays provenance and limitations.
- CI passes on the commit that includes the importer and app integration.

Metadata-only entries and importer scripts without verified generated output do not count as completed manuscript transcriptions.
