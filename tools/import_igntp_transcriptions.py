#!/usr/bin/env python3
"""Download and archive licensed IGNTP Greek manuscript TEI transcriptions.

The original TEI XML is retained unmodified. Each manuscript remains a separate
witness file. Explicitly more restrictive licences in individual TEI headers
are excluded and recorded rather than silently relicensed.
"""
import hashlib
import json
import pathlib
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import io

OUT = pathlib.Path("app/src/main/assets/igntp")
OUT.mkdir(parents=True, exist_ok=True)
XML_NS = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
COLLECTIONS = [
    ("john_igntp_greek", "John — IGNTP Greek", "https://itseeweb.cal.bham.ac.uk/iohannes/downloads/IGNTP_greek_john_transcriptions.zip"),
    ("john_byzantine_greek", "John — Byzantine Greek", "https://itseeweb.cal.bham.ac.uk/iohannes/downloads/Byzantine_john_transcriptions.zip"),
    ("john_family1_greek", "John — Family 1 Greek", "https://itseeweb.cal.bham.ac.uk/iohannes/downloads/Family1_greek_john_transcriptions.zip"),
    ("john_latin", "John — Latin", "https://itseeweb.cal.bham.ac.uk/iohannes/downloads/Latin_john_transcriptions.zip"),
    ("john_coptic", "John — Coptic", "https://itseeweb.cal.bham.ac.uk/iohannes/downloads/coptic_transcriptions_john.zip"),
    ("romans", "Romans", "https://itseeweb.cal.bham.ac.uk/epistulae/downloads/Romans_Greek_transcriptions.zip"),
    ("first_corinthians", "1 Corinthians", "https://itseeweb.cal.bham.ac.uk/epistulae/downloads/1Cor_Greek_transcriptions.zip"),
    ("galatians", "Galatians", "https://itseeweb.cal.bham.ac.uk/epistulae/downloads/Galatians_Greek_transcriptions.zip"),
    ("ephesians", "Ephesians", "https://itseeweb.cal.bham.ac.uk/epistulae/downloads/Ephesians_Greek_transcriptions.zip"),
    ("philippians", "Philippians", "https://itseeweb.cal.bham.ac.uk/epistulae/downloads/Philippians_Greek_transcriptions.zip"),
    ("colossians", "Colossians", "https://itseeweb.cal.bham.ac.uk/epistulae/downloads/Colossians_Greek_transcriptions.zip"),
    ("philemon", "Philemon", "https://itseeweb.cal.bham.ac.uk/epistulae/downloads/Philemon_Greek_transcriptions.zip"),
    ("hebrews", "Hebrews", "https://itseeweb.cal.bham.ac.uk/epistulae/downloads/Hebrews_Greek_transcriptions.zip"),
]
MAX_ARCHIVE = 80 * 1024 * 1024
MAX_MEMBER = 8 * 1024 * 1024
MAX_TOTAL_UNPACKED = 512 * 1024 * 1024

def download(url):
    # The Birmingham server rejects generic/custom client identifiers with HTTP 406.
    # Use a conventional browser request and identify the official download page.
    referer = ("https://itseeweb.cal.bham.ac.uk/iohannes/download.html"
               if "/iohannes/" in url else
               "https://itseeweb.cal.bham.ac.uk/epistulae/download.html")
    req = urllib.request.Request(url, headers={
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64; rv:128.0) "
                       "Gecko/20100101 Firefox/128.0"),
        "Accept": "application/zip,application/octet-stream,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": referer,
        "Connection": "keep-alive"
    })
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                data = response.read(MAX_ARCHIVE + 1)
                if len(data) > MAX_ARCHIVE:
                    raise RuntimeError(f"Archive exceeds size limit: {url}")
                return data
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last = exc
            if attempt < 4:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Download failed: {url}: {last}")

def local_name(tag):
    return tag.rsplit("}", 1)[-1]

def text_of(element):
    return " ".join(t.strip() for t in element.itertext() if t and t.strip())

manifest = {
    "schema_version": 1,
    "provider": "International Greek New Testament Project (IGNTP), University of Birmingham",
    "license_policy": "CC BY 4.0 for the official IGNTP transcription download collections; an individual TEI header declaring a more restrictive licence overrides and causes that file to be excluded.",
    "attribution": "International Greek New Testament Project (IGNTP), Institute for Textual Scholarship and Electronic Editing, University of Birmingham.",
    "collections": [],
    "files": [],
    "excluded_files": [],
    "limitations": [
        "Original TEI XML files are retained unmodified.",
        "Each manuscript is a separate witness; no manuscript readings are merged.",
        "TEI identifiers and source metadata are preserved; a filename is not used as sole proof of manuscript identity.",
        "The 1 Corinthians project remains ongoing; the downloaded archive contains the individual transcriptions currently released by IGNTP, not a completed critical edition."
    ]
}
total_unpacked = 0
for collection_id, work, url in COLLECTIONS:
    archive_bytes = download(url)
    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as exc:
        raise RuntimeError(f"Downloaded source is not a valid ZIP for {work}: {url}") from exc
    collection_records = []
    xml_members = [m for m in archive.infolist() if not m.is_dir() and m.filename.lower().endswith(".xml")]
    if not xml_members:
        raise RuntimeError(f"No TEI XML files found in IGNTP archive: {work}")
    for member in xml_members:
        if member.file_size > MAX_MEMBER:
            raise RuntimeError(f"XML member exceeds size limit: {member.filename}")
        total_unpacked += member.file_size
        if total_unpacked > MAX_TOTAL_UNPACKED:
            raise RuntimeError("Combined IGNTP XML exceeds extraction safety limit")
        raw = archive.read(member)
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            # Preserve source integrity: do not repair or silently rewrite malformed
            # provider XML. Record the exact archive member as excluded and continue.
            manifest["excluded_files"].append({
                "collection": collection_id,
                "archive_member": member.filename,
                "reason": f"Source XML is not well-formed and was not imported: {exc}",
                "source_archive": url
            })
            continue
        if local_name(root.tag) != "TEI":
            raise RuntimeError(f"Unexpected XML root in {work}/{member.filename}: {root.tag}")
        header = root.find(f"{XML_NS}teiHeader")
        if header is None:
            raise RuntimeError(f"TEI header missing in {work}/{member.filename}")
        header_text = text_of(header)
        upper = header_text.upper().replace("-", " ").replace("_", " ")
        restrictive = any(token in upper for token in (
            "CC BY NC", "CC BY NC SA", "CC BY NC ND", "CREATIVE COMMONS ATTRIBUTION NON COMMERCIAL"
        ))
        if restrictive:
            manifest["excluded_files"].append({
                "collection": collection_id,
                "archive_member": member.filename,
                "reason": "Individual TEI header declares a non-commercial or otherwise more restrictive licence; not imported.",
                "source_archive": url
            })
            continue
        xml_id = root.attrib.get(XML_ID) or root.attrib.get("xml:id")
        titles = [text_of(el) for el in header.iter() if local_name(el.tag) == "title" and text_of(el)]
        title = titles[0] if titles else f"IGNTP transcription of {work}"
        document_titles = [text_of(el) for el in header.iter()
                           if local_name(el.tag) == "title" and el.attrib.get("type") == "document" and text_of(el)]
        manuscript_title = document_titles[0] if document_titles else title
        # Keep the relative archive member name but reject traversal and unsafe paths.
        parts = pathlib.PurePosixPath(member.filename).parts
        if any(p in ("..", "") for p in parts) or pathlib.PurePosixPath(member.filename).is_absolute():
            raise RuntimeError(f"Unsafe path in archive: {member.filename}")
        safe_parts = [re.sub(r"[^A-Za-z0-9._-]", "_", p) for p in parts]
        relative = pathlib.Path(collection_id, *safe_parts)
        destination = OUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        record = {
            "work": work,
            "collection": collection_id,
            "archive_member": member.filename,
            "offline_asset": "igntp/" + relative.as_posix(),
            "xml_id": xml_id,
            "title": title,
            "manuscript_title": manuscript_title,
            "license": "CC BY 4.0",
            "license_basis": "Official IGNTP transcription download collection page; no more restrictive licence found in this individual TEI header.",
            "source_archive": url,
            "source_page": ("https://itseeweb.cal.bham.ac.uk/iohannes/download.html"
                            if collection_id.startswith("john_") else
                            "https://itseeweb.cal.bham.ac.uk/epistulae/download.html"),
            "byte_count": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()
        }
        manifest["files"].append(record)
        collection_records.append(record)
    if not collection_records:
        raise RuntimeError(f"No files passed individual licence checks for {work}")
    manifest["collections"].append({
        "id": collection_id,
        "work": work,
        "source_archive": url,
        "xml_file_count": len(collection_records),
        "excluded_restricted_file_count": sum(1 for x in manifest["excluded_files"] if x["collection"] == collection_id)
    })
    print(f"{work}: imported {len(collection_records)} TEI witnesses; excluded "
          f"{sum(1 for x in manifest['excluded_files'] if x['collection'] == collection_id)} restricted files")

if len(manifest["collections"]) != len(COLLECTIONS):
    raise RuntimeError("One or more IGNTP source collections were not imported")
if len(manifest["files"]) < 13:
    raise RuntimeError(f"Unexpectedly small IGNTP import: {len(manifest['files'])} TEI files")
(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Archived {len(manifest['files'])} individual IGNTP TEI witnesses from {len(manifest['collections'])} collections.")
