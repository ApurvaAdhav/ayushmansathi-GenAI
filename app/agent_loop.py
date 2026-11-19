
import re

from app.tools import cover_balance_tracker
from app.vectorstore import semantic_search


def run_agent(user_message):

    # Check for empty input
    if not user_message or not user_message.strip():
        return {
            "tool_used": None,
            "answer": "Please enter a question."
        }

    message = user_message.lower()

    # Tool 1: Cover Balance Tracker
    if any(word in message for word in [
        "balance", "remaining cover", "coverage used",
        "family cover", "claim", "hospital package",
        "package cost", "cover left"
    ]):

        numbers = re.findall(r"\d[\d,]*", message)

        planned_package = 0

        if numbers:
            planned_package = int(numbers[-1].replace(",", ""))

        result = cover_balance_tracker(
            planned_package=planned_package
        )

        return {
            "tool_used": "cover_balance_tracker",
            "result": result
        }

    # Tool 2: RAG Search
    results = semantic_search(
        query=user_message,
        n_results=5
    )

    if not results:
        return {
            "tool_used": "rag_search",
            "answer": "I don't know. No relevant information was found.",
            "citations": []
        }

    citations = []

    for item in results:
        metadata = item.get("metadata", {})

        citations.append({
            "chunk_id": item.get("chunk_id"),
            "document": metadata.get("title"),
            "page": metadata.get("page"),
            "source": metadata.get("source")
        })

    return {
        "tool_used": "rag_search",
        "results": results,
        "citations": citations
    }


if __name__ == "__main__":

    print("AyushmanSathi Agent")
    print("-------------------")

    question = input("Ask your question: ")

    response = run_agent(question)

    print("\nAgent Response:")
    print(response)
