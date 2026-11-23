
from pathlib import Path

from app.chunking import create_chunks
from app.embed import generate_embeddings

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "chroma_db"

client = None
collection = None


# --------------------------------------------------
# 1. Initialize ChromaDB
# --------------------------------------------------

def get_collection():
    global client, collection

    if collection is None:
        import chromadb

        client = chromadb.PersistentClient(
            path=str(DB_PATH)
        )

        collection = client.get_or_create_collection(
            name="ayushmansathi_documents",
            metadata={
                "description": "AyushmanSathi healthcare document chunks"
            }
        )

    return collection


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
        "unspecified surgical procedure package US code, procedures not listed "
        "in the Health Benefit Package HBP, unspecified package guidelines section 1.7, "
        "package rates, pre-authorisation approval criteria, "
        "1 lakh limit unspecified procedure overall limit 5 lakh"
    ),

    "pre-authorisation": (
        "pre-authorization approval required before treatment, "
        "TMS treatment management system, pre-auth request submission, "
        "mandatory documents clinical notes investigation reports"
    ),

    "empanelled hospital": (
        "empanelled health care provider EHCP role responsibilities, "
        "hospital empanelment PM-JAY scheme, cashless treatment provider"
    ),

    "coverage limit": (
        "annual coverage limit PM-JAY family 5 lakh 5,00,000 rupees, "
        "health benefit package sum insured per family per year, "
        "AB PM-JAY beneficiary annual entitlement"
    ),
}


def expand_query(query):
    """Add relevant search terms to specific PM-JAY queries."""

    query_lower = query.lower()

    if (
        "personally eligible" in query_lower
        or "personal eligibility" in query_lower
    ):
        return query + " " + QUERY_EXPANSIONS["personal eligibility"]

    if "unspecified package" in query_lower or "unspecified procedure" in query_lower:
        return query + " " + QUERY_EXPANSIONS["unspecified package"]

    if (
        "pre-authoris" in query_lower
        or "pre authoris" in query_lower
        or "preauthoris" in query_lower
        or "pre-auth" in query_lower
    ):
        return query + " " + QUERY_EXPANSIONS["pre-authorisation"]

    if (
        "empanelled hospital" in query_lower
        or "empaneled hospital" in query_lower
        or "role of" in query_lower
    ):
        return query + " " + QUERY_EXPANSIONS["empanelled hospital"]

    if (
        "annual coverage limit" in query_lower
        or "coverage limit" in query_lower
        or "annual limit" in query_lower
        or "maximum" in query_lower
    ):
        return query + " " + QUERY_EXPANSIONS["coverage limit"]

    return query


# --------------------------------------------------
# 3. HBP Version Priority
# --------------------------------------------------

def version_priority(version):
    """Convert an HBP version into a sortable numeric value."""

    if not version or version == "Unknown":
        return (0,)

    try:
        return tuple(
            int(part) for part in version.split(".")
        )
    except ValueError:
        return (0,)


def ranking_score(result):
    """
    Keep semantic relevance primary while giving newer
    HBP versions a small preference.
    """

    distance = result["distance"]
    version = result["metadata"].get("version", "Unknown")

    priority = version_priority(version)

    version_bonus = 0.0

    if priority != (0,):
        version_value = sum(
            value / (10 ** index)
            for index, value in enumerate(priority)
        )

        version_bonus = min(0.02, version_value * 0.005)

    return distance - version_bonus


# --------------------------------------------------
# 4. Store Document Chunks and Embeddings
# --------------------------------------------------

def store_chunks(chunk_size=1000, overlap=150):
    """Rebuild ChromaDB with document and version metadata."""

    collection = get_collection()

    chunks = create_chunks(
        chunk_size=chunk_size,
        overlap=overlap
    )

    if not chunks:
        print("No chunks available to store.")
        return

    existing = collection.get(include=["metadatas"])
    existing_ids = existing.get("ids", [])

    if existing_ids:
        collection.delete(ids=existing_ids)

    texts = [
        chunk["text"] for chunk in chunks
    ]

    embeddings = generate_embeddings(texts)

    ids = [
        chunk["chunk_id"] for chunk in chunks
    ]

    metadatas = [
        {
            "title": chunk["title"],
            "source": chunk["source"],
            "page": chunk["page"],
            "section": chunk["section"],
            "version": chunk["version"],
            "rule_topic": chunk["rule_topic"]
        }
        for chunk in chunks
    ]

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

    versions = {}

    for chunk in chunks:
        version = chunk["version"]
        versions[version] = versions.get(version, 0) + 1

    print("Document versions:", versions)


# --------------------------------------------------
# 5. Semantic Search
# --------------------------------------------------

def semantic_search(query, n_results=5, distance_threshold=1.2):
    """Retrieve relevant chunks with HBP version preference.

    Chunks with a cosine distance above ``distance_threshold`` are
    discarded before being sent to the LLM.  The default of 1.2 is
    deliberately permissive — it removes only chunks that share
    virtually no vocabulary with the query.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if n_results < 1:
        raise ValueError("n_results must be at least 1.")

    collection = get_collection()

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    expanded_query = expand_query(query)

    query_embedding = generate_embeddings(
        [expanded_query]
    )[0]

    candidate_count = min(
        max(n_results * 5, 20),
        total_chunks
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_count,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    search_results = []

    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        # Drop chunks that are too far from the query.
        if distance <= distance_threshold:
            search_results.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": distance
            })

    # Sort by semantic relevance with a small version preference.
    search_results.sort(key=ranking_score)

    return search_results[:min(n_results, total_chunks)]


# --------------------------------------------------
# 6. Test the Vector Database
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

            metadata = result["metadata"]

            print(f"\nResult {index}")
            print("Chunk ID:", result["chunk_id"])
            print("Text:", result["text"])
            print("Source:", metadata["title"])
            print("Version:", metadata["version"])
            print("Section:", metadata["section"])
            print("Page:", metadata["page"])
            print("Distance:", result["distance"])
