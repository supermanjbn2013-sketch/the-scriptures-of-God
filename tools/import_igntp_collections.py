#!/usr/bin/env python3
"""Import openly licensed IGNTP TEI manuscript transcription collections.

The official IGNTP transcription page states CC BY 4.0 reuse. Any XML file
carrying an explicit incompatible licence is excluded. Only XML witnesses
that pass the licence check are copied into sanitized offline ZIP archives.
The original TEI markup is preserved; a separate block index is a search aid,
not a replacement for the diplomatic XML.
"""
import hashlib
import html
import io
import json
import pathlib
import re
import time
import urllib.error
import urllib.request
import zipfile
import gzip
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = pathlib.Path("app/src/main/assets/igntp")
ARCHIVES = ROOT / "archives"
INDEXES = ROOT / "indexes"
USER_AGENT = "The-Scriptures-of-God-Archive/1.0"
LICENSE = "CC BY 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
TRANSCRIPTIONS_PAGE = "https://itseeweb.cal.bham.ac.uk/igntp/transcriptions.html"
PAUL_DOWNLOAD_PAGE = "https://itseeweb.cal.bham.ac.uk/epistulae/download.html"
JOHN_DOWNLOAD_PAGE = "https://itseeweb.cal.bham.ac.uk/iohannes/download.html"

COLLECTIONS = [
    ("paul-romans", "Greek Romans transcriptions", PAUL_DOWNLOAD_PAGE, "Romans", "grc"),
    ("paul-galatians", "Greek Galatians transcriptions", PAUL_DOWNLOAD_PAGE, "Galatians", "grc"),
    ("paul-ephesians", "Greek Ephesians transcriptions", PAUL_DOWNLOAD_PAGE, "Ephesians", "grc"),
    ("paul-philippians", "Greek Philippians transcriptions", PAUL_DOWNLOAD_PAGE, "Philippians", "grc"),
    ("paul-colossians", "Greek Colossians transcriptions", PAUL_DOWNLOAD_PAGE, "Colossians", "grc"),
    ("paul-philemon", "Greek Philemon transcriptions", PAUL_DOWNLOAD_PAGE, "Philemon", "grc"),
    ("paul-hebrews", "Greek Hebrews transcriptions", PAUL_DOWNLOAD_PAGE, "Hebrews", "grc"),
    ("paul-1-corinthians", "Greek 1 Corinthians transcriptions", PAUL_DOWNLOAD_PAGE, "1 Corinthians", "grc"),
    ("john-igntp-greek", "Download IGNTP Greek transcriptions of John", JOHN_DOWNLOAD_PAGE, "John", "grc"),
    ("john-byzantine-greek", "Download Byzantine transcriptions of John", JOHN_DOWNLOAD_PAGE, "John", "grc"),
    ("john-family-1-greek", "Download Family 1 transcriptions of John", JOHN_DOWNLOAD_PAGE, "John", "grc"),
    ("john-latin", "Download Latin transcriptions of John", JOHN_DOWNLOAD_PAGE, "John", "la"),
    ("john-coptic", "Download Coptic transcriptions of John", JOHN_DOWNLOAD_PAGE, "John", "cop"),
]

XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_href = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_data(self, data):
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.current_href is not None:
            label = " ".join("".join(self.current_text).split())
            self.links.append((label, self.current_href))
            self.current_href = None
            self.current_text = []


def fetch(url, attempts=5):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in (408, 425, 429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            last_error = error
        if attempt + 1 < attempts:
            delay = min(4 * (2 ** attempt), 45)
            print(f"Temporary download failure; retrying in {delay}s: {url} ({last_error})", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"Download failed after {attempts} attempts: {url}: {last_error}")


def resolve_download(page_url, expected_label):
    parser = AnchorParser()
    parser.feed(fetch(page_url).decode("utf-8", "replace"))
    wanted = re.sub(r"\s+", " ", expected_label).strip().casefold()
    matches = [(label, href) for label, href in parser.links
               if re.sub(r"\s+", " ", label).strip().casefold() == wanted]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one download link named {expected_label!r} on {page_url}; found {len(matches)}"
        )
    return urllib.parse.urljoin(page_url, matches[0][1])


def local_name(tag):
    return tag.rsplit("}", 1)[-1].lower()


def text_of(elem):
    return " ".join(" ".join(elem.itertext()).split())


def xml_license(root):
    header = next((node for node in root.iter() if local_name(node.tag) == "teiheader"), None)
    if header is None:
        return "inherited", "No per-file licence element; inherited from official IGNTP transcription reuse statement"
    statements = []
    for node in header.iter():
        if local_name(node.tag) not in ("licence", "license"):
            continue
        target = " ".join(str(v) for k, v in node.attrib.items() if k.lower() in ("target", "href", "url"))
        body = text_of(node)
        statements.append((target + " " + body).strip())
    if not statements:
        return "inherited", "No per-file licence element; inherited from official IGNTP transcription reuse statement"
    combined = " ".join(statements).casefold().replace(" ", "")
    if any(term in combined for term in (
        "by-nc", "bynd", "by-sa", "allrightsreserved", "copyright"
    )):
        return "excluded", "Explicit per-file terms are not the archive's CC BY 4.0 reuse licence"
    if "creativecommons.org/licenses/by/4.0" in combined or "ccby4.0" in combined:
        return "accepted", "Explicit per-file CC BY 4.0 statement"
    return "excluded", "Explicit per-file licence could not be verified as CC BY 4.0"


def first_text(root, names):
    wanted = set(names)
    for node in root.iter():
        if local_name(node.tag) in wanted:
            value = text_of(node)
            if value:
                return value
    return ""


def marker(elem):
    return elem.attrib.get(XML_ID) or elem.attrib.get("n") or elem.attrib.get("id") or ""


def collect_blocks(root, collection, witness_id, xml_member, license_basis):
    body = next((node for node in root.iter() if local_name(node.tag) == "body"), root)
    blocks = [node for node in body.iter() if local_name(node.tag) == "ab"]
    if not blocks:
        blocks = [node for node in body.iter() if local_name(node.tag) == "p"]
    if not blocks:
        blocks = [body]

    rows = []
    for ordinal, block in enumerate(blocks, 1):
        source_text = []
        page_ids, column_ids, line_ids = [], [], []
        for node in block.iter():
            tag = local_name(node.tag)
            if tag == "note":
                continue
            if tag == "pb":
                value = marker(node)
                if value and value not in page_ids:
                    page_ids.append(value)
            elif tag == "cb":
                value = marker(node)
                if value and value not in column_ids:
                    column_ids.append(value)
            elif tag == "lb":
                value = marker(node)
                if value and value not in line_ids:
                    line_ids.append(value)
            if node.text and tag not in ("note",):
                source_text.append(node.text)
            if node.tail:
                source_text.append(node.tail)
        plain = " ".join("".join(source_text).split())
        if not plain:
            continue
        rows.append({
            "collection_id": collection["id"],
            "collection_title": collection["title"],
            "work": collection["work"],
            "language": collection["language"],
            "witness_id": witness_id,
            "witness_title": first_text(root, ("title",)),
            "xml_member": xml_member,
            "source_label": marker(block) or str(ordinal),
            "page_ids": page_ids,
            "column_ids": column_ids,
            "line_ids": line_ids,
            "text": plain,
            "license": LICENSE,
            "license_basis": license_basis,
            "source_transcription": "IGNTP TEI XML; original XML is retained in the matching offline collection archive"
        })
    return rows


def safe_member(name):
    name = name.replace("\\", "/")
    parts = pathlib.PurePosixPath(name).parts
    return bool(name.lower().endswith(".xml")) and not name.startswith("/") and ".." not in parts


def main():
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    INDEXES.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "record_type": "igntp_tei_transcription_collection_manifest",
        "license": LICENSE,
        "license_url": LICENSE_URL,
        "license_policy": "Only CC BY 4.0 XML witnesses are imported. Explicit incompatible or unclear per-file licences are excluded. Where an XML file has no per-file licence element, the official IGNTP collection-level CC BY 4.0 reuse statement is recorded as the basis.",
        "official_transcription_page": TRANSCRIPTIONS_PAGE,
        "collections": []
    }
    expected_ids = {item[0] for item in COLLECTIONS}
    total_witnesses = 0
    total_blocks = 0

    for collection_id, label, page_url, work, language in COLLECTIONS:
        collection = {"id": collection_id, "title": label, "work": work, "language": language}
        download_url = resolve_download(page_url, label)
        archive_bytes = fetch(download_url)
        source_sha = hashlib.sha256(archive_bytes).hexdigest()
        source_zip = zipfile.ZipFile(io.BytesIO(archive_bytes))
        output_path = ARCHIVES / (collection_id + ".zip")
        records_path = INDEXES / (collection_id + ".jsonl.gz")
        witnesses = []
        excluded = []
        rows = []
        accepted_files = []

        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as sanitized:
            for info in source_zip.infolist():
                if info.is_dir() or not safe_member(info.filename):
                    continue
                if info.file_size > 40 * 1024 * 1024:
                    excluded.append({"member": info.filename, "reason": "XML member exceeds 40 MiB safety limit"})
                    continue
                raw_xml = source_zip.read(info)
                try:
                    root = ET.fromstring(raw_xml)
                except ET.ParseError as error:
                    excluded.append({"member": info.filename, "reason": "XML parse failure: " + str(error)})
                    continue
                status, basis = xml_license(root)
                if status == "excluded":
                    excluded.append({"member": info.filename, "reason": basis})
                    continue
                # Keep only the verified XML witness files, not unreviewed ancillary archive contents.
                sanitized.writestr(info.filename, raw_xml)
                witness_id = root.attrib.get(XML_ID) or pathlib.PurePosixPath(info.filename).stem
                witness_title = first_text(root, ("title",)) or witness_id
                block_rows = collect_blocks(root, collection, witness_id, info.filename, basis)
                rows.extend(block_rows)
                witnesses.append({
                    "witness_id": witness_id,
                    "title": witness_title,
                    "xml_member": info.filename,
                    "xml_sha256": hashlib.sha256(raw_xml).hexdigest(),
                    "xml_bytes": len(raw_xml),
                    "license": LICENSE,
                    "license_basis": basis,
                    "text_block_count": len(block_rows)
                })
                accepted_files.append(info.filename)

        if not witnesses:
            output_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"No eligible CC BY 4.0 TEI witnesses imported for {collection_id}. "
                f"Review source page and per-file licence metadata."
            )

        with gzip.open(records_path, "wt", encoding="utf-8", newline="\n", compresslevel=9) as output:
            for row in rows:
                output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

        collection_record = {
            "id": collection_id,
            "title": label,
            "work": work,
            "language": language,
            "download_page": page_url,
            "download_url": download_url,
            "source_archive_sha256": source_sha,
            "offline_archive": "igntp/archives/" + output_path.name,
            "offline_index": "igntp/indexes/" + records_path.name,
            "witness_count": len(witnesses),
            "text_block_count": len(rows),
            "accepted_xml_members": accepted_files,
            "excluded_members": excluded,
            "witnesses": witnesses,
            "source_handling": "Original TEI XML preserved unchanged inside the sanitized ZIP. The JSONL index is a flattened search aid and does not replace the diplomatic transcription."
        }
        manifest["collections"].append(collection_record)
        total_witnesses += len(witnesses)
        total_blocks += len(rows)
        print(f"{collection_id}: {len(witnesses)} witnesses, {len(rows)} indexed text blocks, {len(excluded)} excluded")

    actual_ids = {item["id"] for item in manifest["collections"]}
    if actual_ids != expected_ids or len(manifest["collections"]) != 13:
        raise RuntimeError(f"Collection inventory mismatch: missing={expected_ids-actual_ids}, unexpected={actual_ids-expected_ids}")

    manifest["collection_count"] = len(manifest["collections"])
    manifest["witness_count"] = total_witnesses
    manifest["text_block_count"] = total_blocks
    (ROOT / "igntp_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "SOURCE_NOTICE.txt").write_text(
        "International Greek New Testament Project (IGNTP) electronic transcriptions.\n"
        "Reuse: Creative Commons Attribution 4.0 International (CC BY 4.0).\n"
        "Official transcription page: " + TRANSCRIPTIONS_PAGE + "\n"
        "XML source files with explicit incompatible or unclear per-file licences are excluded.\n"
        "Original TEI XML files are preserved unchanged inside the sanitized offline ZIP archives.\n"
        "The generated JSONL indexes are flattened search aids, not replacements for the TEI XML.\n",
        encoding="utf-8"
    )
    print(f"Imported {len(manifest['collections'])} IGNTP collections, {total_witnesses} witnesses, {total_blocks} indexed blocks.")


if __name__ == "__main__":
    import urllib.parse
    main()
