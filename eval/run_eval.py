
import json
import re
from pathlib import Path

from app.vectorstore import semantic_search, store_chunks

BASE_DIR = Path(__file__).resolve().parent.parent

EVAL_FILE = BASE_DIR / "eval" / "eval_set.json"
RESULT_FILE = BASE_DIR / "eval" / "config_results.json"

CONFIGURATIONS = [
    {
        "name": "Configuration A",
        "chunk_size": 500,
        "top_k": 3
    },
    {
        "name": "Configuration B",
        "chunk_size": 1000,
        "top_k": 5
    }
]

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "in", "on", "at", "to", "of", "for", "and",
    "or", "under", "with", "by", "from", "can",
    "be", "do", "does", "i", "you", "your",
    "it", "this", "that", "up", "per", "as",
    "what", "how", "when", "who", "which",
    "don't", "not", "know", "rs"
}


def load_questions():
    with open(EVAL_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_expected_terms(item):
    """Read expected terms from either supported dataset format."""

    expected_keywords = item.get("expected_keywords")

    if expected_keywords:
        if isinstance(expected_keywords, str):
            expected_keywords = [expected_keywords]

        return [
            term.lower().strip()
            for term in expected_keywords
            if term.strip()
        ]

    expected = item.get("expected", "")

    if not isinstance(expected, str):
        return []

    if expected.strip().lower() in {
        "i don't know",
        "i do not know"
    }:
        return []

    words = re.findall(r"\b[\w]+\b", expected.lower())

    return [
        word for word in words
        if word not in STOP_WORDS
    ]


def evaluate_configuration(questions, config):
    print(f"\nRunning {config['name']}")
    print("-" * 50)

    store_chunks(
        chunk_size=config["chunk_size"],
        overlap=150
    )

    results = []

    for item in questions:
        question = item["question"]
        expected_terms = get_expected_terms(item)

        try:
            retrieved = semantic_search(
                question,
                n_results=config["top_k"]
            )

            retrieved_text = " ".join(
                chunk["text"] for chunk in retrieved
            ).lower()

            matched_terms = [
                term for term in expected_terms
                if term in retrieved_text
            ]

            if expected_terms:
                score = len(matched_terms) / len(expected_terms)
            else:
                score = None

            result = {
                "id": item["id"],
                "question": question,
                "expected": item.get("expected", ""),
                "expected_terms": expected_terms,
                "matched_terms": matched_terms,
                "keyword_score": (
                    round(score, 4) if score is not None else None
                ),
                "retrieved_chunks": len(retrieved),
                "citations_available": bool(retrieved)
            }

            results.append(result)

            score_display = (
                f"{score:.2f}" if score is not None else "N/A"
            )

            print(
                f"Q{item['id']}: Score = {score_display}, "
                f"Chunks = {len(retrieved)}"
            )

        except Exception as error:  # noqa: BLE001
            print(f"Q{item['id']} failed: {error}")

            results.append({
                "id": item["id"],
                "question": question,
                "error": str(error),
                "keyword_score": None,
                "retrieved_chunks": 0,
                "citations_available": False
            })

    scored_results = [
        result for result in results
        if result.get("keyword_score") is not None
    ]

    average_score = (
        sum(r["keyword_score"] for r in scored_results)
        / len(scored_results)
        if scored_results else 0
    )

    citation_rate = (
        sum(
            1 for result in results
            if result["citations_available"]
        ) / len(questions)
        if questions else 0
    )

    return {
        "configuration": config,
        "total_questions": len(questions),
        "scored_questions": len(scored_results),
        "average_keyword_score": round(average_score, 4),
        "citation_rate": round(citation_rate, 4),
        "results": results
    }


def main():
    questions = load_questions()
    all_results = []

    try:
        for config in CONFIGURATIONS:
            evaluation = evaluate_configuration(
                questions,
                config
            )

            all_results.append(evaluation)

    finally:
        print("\nRestoring default ChromaDB index...")

        store_chunks(
            chunk_size=1000,
            overlap=150
        )

    if not all_results:
        print("No evaluation results were generated.")
        return

    scores = [
        result["average_keyword_score"]
        for result in all_results
    ]

    if scores[0] > scores[1]:
        winner = "Configuration A"
    elif scores[1] > scores[0]:
        winner = "Configuration B"
    else:
        winner = "Tie"

    report = {
        "total_questions": len(questions),
        "configurations": all_results,
        "winner": winner
    }

    with open(RESULT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========== EVALUATION SUMMARY ==========")

    for result in all_results:
        config = result["configuration"]

        print(f"\n{config['name']}")
        print("Chunk size:", config["chunk_size"])
        print("Top K:", config["top_k"])
        print(
            "Average keyword score:",
            result["average_keyword_score"]
        )
        print(
            "Scored questions:",
            result["scored_questions"]
        )
        print(
            "Citation rate:",
            result["citation_rate"]
        )

    print("\nWinner:", winner)
    print("Detailed results saved to:", RESULT_FILE)


if __name__ == "__main__":
    main()
