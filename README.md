# The Scriptures of God

An Android-first, offline-capable research archive for ancient scriptural texts, manuscript witnesses, textual forms, and source comparisons.

## Project principles

- Free access, with voluntary donations only. No mandatory subscription, paid tier, or paywall.
- No login screen. The app is intended to open and be used directly.
- Text-first development. Searchable text, source attribution, witness identity, and coverage audits take priority over manuscript photographs and facsimiles.
- Distinguish an edited edition from a diplomatic transcription of a particular manuscript.
- Never invent missing readings or imply that a manuscript preserves a whole book when only fragments survive.
- Preserve source coordinates, editorial marks, corrections, provenance, and licence notices.

## Current text corpus

The build process generates an offline JSONL corpus from the source repositories. The current collection includes:

- Hebrew text based on the Westminster Leningrad Codex through the Open Scriptures Hebrew Bible project.
- Greek Apostolic Writings from the SBL Greek New Testament v1.2. This is an edited Greek text, not a transcription of P46, P52, P66, P75, Codex Vaticanus, or Codex Sinaiticus.
- Greek Apocrypha and Deuterocanonical texts from Henry Barclay Swete's Septuagint edition as digitized by Open Greek and Latin First1KGreek.
- Separate Old Greek and Theodotionic forms for Susanna, Daniel, and Bel and the Dragon.
- Latin transmission texts for 2 Esdras / 4 Ezra (the 16-chapter composite containing 5 Ezra, 4 Ezra proper, and 6 Ezra) and the Latin Prayer of Manasseh.
- A separate Greek Prayer of Manasseh text indexed from Odes 8.

The Apocrypha import currently covers 23 named books or textual forms. The generated `apocrypha_coverage.json` records the actual chapter and source-verse coverage of each imported digital source file. That inventory does not establish a universal canon, nor does it imply that all ancient manuscript witnesses survive.

## Manuscript archive

The catalogue includes selected Dead Sea Scrolls metadata and passage concordances. Some Qumran-Digital transcriptions and published passage mappings are imported line by line where the source provides explicit coordinates. Digital display-line numbers are not silently converted into manuscript column or line numbers.

The Codex Sinaiticus Project's electronic transcription has been located and catalogued separately. Its XML is a manuscript-based transcription with page, column, line, correction, and marginal-text markup. It is not yet bundled in the offline corpus. Its transcription licence is CC BY-NC-SA 3.0; any later import must preserve that non-commercial, share-alike licence and the XML's manuscript structure.

The Way to Yahuweh downloads are evaluated file by file. Each transcription must retain its own manuscript identifier, underlying edition, coverage, source URL, licence, and editorial cautions.

## Search and reader

- Exact word and exact phrase search across the imported verse text, book names, references, original source coordinates, and indexed DSS transcription lines.
- Search results are capped at 100 per query.
- Book readers load text in a background task and show source, edition, witness basis, textual form, transcription type, licence, attribution, and source links.
- Apocrypha readers display the source-file chapter coverage audit.
- The DSS passage concordance keeps transcription editions separate. The 4Q47 Joshuaᵃ entry now includes later fragment-group transcription blocks from The Way to Yahuweh alongside, but not merged with, the Qumran-Digital line map. The source blocks retain fragment headings, passage cautions, attribution, and CC BY-SA 4.0 terms.
- Each imported Hebrew- or Greek-language verse is individually selectable; tapping it automatically translates the verse into the saved target language.
- The target-language selector includes all 59 languages listed by the ML Kit on-device translation engine, including Filipino/Tagalog.
- Models download on first use (approximately 30 MB per language model) and remain available offline on the device. Model downloads require an initial internet connection.
- Translation is a machine-generated study aid, not a manuscript reading or a critical translation. The models are designed for modern-language translation, so results from ancient Hebrew or Koine Greek may be inaccurate. Non-English language pairs may use English as an intermediate language.
- Latin source text is not yet supported by the on-device translation engine.
- Translation engine documentation: https://developers.google.com/ml-kit/language/translation/android

## Data sources and licences

Each dataset has its own licence. Do not assume that one licence applies to the whole archive.

- OSHB/WLC: WLC base text is public domain; OSHB annotations are CC BY 4.0.
- SBLGNT v1.2: CC BY 4.0.
- First1KGreek / nathans/lxx-swete transcription: CC BY-SA 4.0.
- Latin Library texts: public-domain status is stated by the Latin Library source; the source does not identify a modern critical edition.
- Codex Sinaiticus electronic transcription: CC BY-NC-SA 3.0; not yet bundled.
- Institutional manuscript images remain on their source websites unless reuse permissions are verified.

Attribution and licence notices are generated in `app/src/main/assets/corpus/SOURCE_NOTICES.txt`.

## Validation

The corpus validation workflow fetches the licensed source texts, generates the offline corpus and coverage audit, then checks:

1. Hebrew and Greek base corpus structure and reference uniqueness.
2. Apocrypha book coverage, source coordinates, licences, and chapter audit.
3. DSS metadata and passage concordance integrity.
4. Android navigation and exact search implementation.

The Android source validation workflow compiles the application without producing an APK. The APK workflow is separate and must not be run until the data and app are ready for a complete release.

## Repository layout

- `app/src/main/java/org/scripturesofgod/archive/MainActivity.java` — Android application.
- `app/src/main/assets/catalog/` — source catalogue, manuscript registers, and DSS concordances.
- `tools/prepare_corpus.py` — reproducible source retrieval and corpus generation.
- `tools/validate_corpus.py` — data and navigation validation.
- `.github/workflows/` — corpus validation, Android source compilation, and eventual APK workflow.

