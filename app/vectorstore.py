
from pathlib import Path

import chromadb

from app.chunking import create_chunks
from app.embed import generate_embeddings

# --------------------------------------------------
# 1. Initialize ChromaDB
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "chroma_db"

client = chromadb.PersistentClient(path=str(DB_PATH))

collection = client.get_or_create_collection(
    name="ayushmansathi_documents",
    metadata={
        "description": "AyushmanSathi healthcare document chunks"
    }
)


# --------------------------------------------------
# 2. Query Expansion
# --------------------------------------------------

QUERY_EXPANSIONS = {
    "personal eligibility": (
        "PM-JAY beneficiary identification process, SECC database, "
        "eligible rural and urban families, beneficiary list, "
        "eligibility verification and authorized beneficiary checking"
    ),

    "unspecified package": (
        "unspecified surgical procedure package, procedures not listed "
        "in the Health Benefit Package HBP, unspecified package guidelines, "
        "package rates, pre-authorisation and approval criteria"
    )
}


def expand_query(query):
    """Add relevant search terms to specific PM-JAY queries."""

    query_lower = query.lower()

    if (
        "personally eligible" in query_lower
        or "personal eligibility" in query_lower
    ):
        return (
            query + " " +
            QUERY_EXPANSIONS["personal eligibility"]
        )

    if "unspecified package" in query_lower:
        return (
            query + " " +
            QUERY_EXPANSIONS["unspecified package"]
        )

    return query


# --------------------------------------------------
# 3. Store Document Chunks and Embeddings
# --------------------------------------------------

def store_chunks(chunk_size=1000, overlap=150):
    """
    Create chunks using the selected configuration
    and rebuild the ChromaDB collection.
    """

    chunks = create_chunks(
        chunk_size=chunk_size,
        overlap=overlap
    )

    if not chunks:
        print("No chunks available to store.")
        return

    # Delete existing chunks before rebuilding the index.
    existing = collection.get(include=["metadatas"])
    existing_ids = existing.get("ids", [])

    if existing_ids:
        collection.delete(ids=existing_ids)

    # Prepare documents, embeddings and IDs.
    texts = [chunk["text"] for chunk in chunks]

    embeddings = generate_embeddings(texts)

    ids = [chunk["chunk_id"] for chunk in chunks]

    # Prepare metadata.
    metadatas = [
        {
            "title": chunk["title"],
            "source": chunk["source"],
            "page": chunk["page"],
            "rule_topic": chunk["rule_topic"]
        }
        for chunk in chunks
    ]

    # Store in ChromaDB.
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("\nChunks stored successfully!")
    print("Chunk size:", chunk_size)
    print("Overlap:", overlap)
    print("Total stored chunks:", collection.count())


# --------------------------------------------------
# 4. Semantic Search
# --------------------------------------------------

def semantic_search(query, n_results=5):
    """
    Retrieve the most relevant chunks using
    semantic similarity.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    n_results = min(n_results, total_chunks)

    # Expand the query.
    expanded_query = expand_query(query)

    # Generate query embedding.
    query_embedding = generate_embeddings(
        [expanded_query]
    )[0]

    # Search ChromaDB.
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    search_results = []

    for i in range(len(results["ids"][0])):

        search_results.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return search_results


# --------------------------------------------------
# 5. Test the Vector Database
# --------------------------------------------------

if __name__ == "__main__":

    store_chunks()

    test_questions = [
        "Can you verify whether I am personally eligible for the PM-JAY scheme?",
        "When can an unspecified package be used under PM-JAY?"
    ]

    for question in test_questions:

        print("\nQuestion:", question)

        results = semantic_search(question)

        for index, result in enumerate(results, start=1):

            print(f"\nResult {index}")
            print("Chunk ID:", result["chunk_id"])
            print("Text:", result["text"])
            print("Source:", result["metadata"]["title"])
            print("Page:", result["metadata"]["page"])
            print("Distance:", result["distance"])
