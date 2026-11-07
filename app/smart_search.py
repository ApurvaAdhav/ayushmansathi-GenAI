
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "records.json"


def smart_search(query, top_k=5):
    # Load records
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    if not records or not query.strip():
        return []

    # Prepare searchable text
    documents = [
        record["rule_topic"] + " " + record["rule_text"] + " " + record["applies_to"]
        for record in records
    ]

    # Convert text into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Convert user query into a vector
    query_vector = vectorizer.transform([query])

    # Calculate cosine similarity
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Rank records by similarity
    ranked_indices = scores.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:
        if scores[index] > 0:
            record = records[index].copy()
            record["similarity_score"] = round(float(scores[index]), 4)
            results.append(record)

    return results
