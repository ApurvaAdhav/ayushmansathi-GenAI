
import re

from app.records import load_records

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = " ".join(text.split())

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def extract_version(title, text=""):
    """Identify the Health Benefit Package version."""

    content = f"{title} {text}"

    match = re.search(
        r"(?:HBP|Health Benefit Package)\s*[-:]?\s*(\d+(?:\.\d+)*)",
        content,
        re.IGNORECASE
    )

    return match.group(1) if match else "Unknown"


def extract_section(record):
    """Preserve section information separately from page information."""

    section = (
        record.get("section")
        or record.get("section_title")
        or record.get("rule_topic")
        or ""
    )

    return str(section).strip() or "Not specified"


def create_chunks(chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    records = load_records()
    all_chunks = []

    for record in records:
        title = record.get("document_title", "Unknown document")
        text_chunks = split_text(
            record["rule_text"],
            chunk_size=chunk_size,
            overlap=overlap
        )

        version = extract_version(title, record["rule_text"])
        section = extract_section(record)

        for index, chunk in enumerate(text_chunks, start=1):
            all_chunks.append({
                "chunk_id": f'{record["id"]}_{index}',
                "text": chunk,
                "title": title,
                "source": record.get("source_url", ""),
                "page": record.get("page_or_section", "Not specified"),
                "section": section,
                "version": version,
                "rule_topic": record.get("rule_topic", "")
            })

    return all_chunks


if __name__ == "__main__":
    chunks = create_chunks()

    print("Total chunks:", len(chunks))

    if chunks:
        print("\nFirst chunk:")
        print(chunks[0])
