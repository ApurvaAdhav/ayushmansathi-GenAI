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


def create_chunks():
    records = load_records()
    all_chunks = []

    for record in records:
        text_chunks = split_text(record["rule_text"])

        for index, chunk in enumerate(text_chunks, start=1):
            all_chunks.append({
                "chunk_id": f'{record["id"]}_{index}',
                "text": chunk,
                "title": record["document_title"],
                "source": record["source_url"],
                "page": record["page_or_section"],
                "rule_topic": record["rule_topic"]
            })

    return all_chunks


if __name__ == "__main__":
    chunks = create_chunks()

    print("Total chunks:", len(chunks))
    print("\nFirst chunk:")
    print(chunks[0])
