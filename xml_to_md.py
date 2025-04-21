# rag_pipeline/xml_to_md.py

import pathlib
import re
from lxml import etree

def sanitize_filename(name):
    return re.sub(r'[\/:"*?<>|]+', "_", name)

def parse_xml_to_markdown_with_metadata(xml_path):
    try:
        with open(xml_path, 'rb') as f:
            tree = etree.parse(f)

        metadata = {
            "title": "",
            "authors": [],
            "doi": "",
        }

        # Extract title
        title_elem = tree.find(".//article-title")
        if title_elem is not None:
            full_title = title_elem.xpath("string()")
            metadata["title"] = full_title.strip()

        # Extract DOI
        doi_elem = tree.find(".//article-id[@pub-id-type='doi']")
        if doi_elem is not None and doi_elem.text:
            metadata["doi"] = "https://doi.org/" + doi_elem.text.strip()

        # Extract authors
        authors = []
        for contrib in tree.findall(".//contrib[@contrib-type='author']"):
            name = contrib.find('name')
            if name is not None:
                given = name.findtext('given-names', default='')
                surname = name.findtext('surname', default='')
                full_name = f"{given} {surname}".strip()
                if full_name:
                    authors.append(full_name)
        metadata["authors"] = ", ".join(authors)

        # Extract body content
        sections = tree.xpath('//body//sec')
        text_parts = []

        for sec in sections:
            title = sec.findtext('title')
            if title:
                text_parts.append(f"### {title.strip()}")
            paragraphs = sec.findall('p')
            for p in paragraphs:
                if p.text and p.text.strip():
                    text_parts.append(p.text.strip())

        markdown_text = "\n\n".join(text_parts)
        return markdown_text, metadata

    except Exception as e:
        print(f"Error parsing {xml_path.name}: {e}")
        return None

def process_scientific_xmls(data_directory, output_directory):
    data_path = pathlib.Path(data_directory)
    output_path = pathlib.Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    metadata_records = []

    xml_files = list(data_path.glob("**/fulltext.xml"))
    for xml_file in xml_files:
        print(f"Processing {xml_file.name} ...")

        if xml_file.stat().st_size == 0:
            print(f"Skipped: {xml_file.name} (Empty file)")
            continue

        result = parse_xml_to_markdown_with_metadata(xml_file)
        if result is None:
            continue
        raw_text, metadata = result

        sanitized_name = sanitize_filename(xml_file.parent.name)
        final_filename = output_path / f"{sanitized_name}_final.md"

        if raw_text.strip():
            final_filename.write_text(raw_text, encoding="utf-8")
            print(f"Saved: {final_filename.name}")
            metadata["filename"] = final_filename.name
            metadata_records.append((final_filename, metadata))
        else:
            print(f"Skipped: {xml_file.name} (No extractable content)")

    return metadata_records

