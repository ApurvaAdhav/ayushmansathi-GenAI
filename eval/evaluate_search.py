
from pathlib import Path

from data.user_questions import user_questions
from app.vectorstore import semantic_search


# Output file
OUTPUT_FILE = Path(__file__).resolve().parent / "search_results.md"


def evaluate_search():
    report = []

    report.append("# Day 7 - Semantic Search Evaluation\n")
    report.append("Model: all-MiniLM-L6-v2\n")
    report.append("Vector Database: ChromaDB\n")
    report.append("Top Results: 5\n")

    for index, question in enumerate(user_questions, start=1):

        print(f"Evaluating question {index}/10...")

        results = semantic_search(question, n_results=5)

        report.append(f"\n## Question {index}: {question}\n")
        report.append(f"Retrieved Results: {len(results)}\n")

        if not results:
            report.append("No results found.\n")
            continue

        for rank, result in enumerate(results, start=1):

            metadata = result["metadata"]

            report.append(f"\n### Result {rank}\n")
            report.append(f"- **Chunk ID:** {result['chunk_id']}\n")
            report.append(f"- **Document:** {metadata['title']}\n")
            report.append(f"- **Page:** {metadata['page']}\n")
            report.append(f"- **Topic:** {metadata['rule_topic']}\n")
            report.append(f"- **Distance:** {result['distance']:.4f}\n")
            report.append(f"\n**Retrieved Text:**\n\n{result['text']}\n")

        report.append("\n---\n")

    OUTPUT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\nEvaluation completed!")
    print("Questions evaluated:", len(user_questions))
    print("Results saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    evaluate_search()
