
import json
import re

from app.llm import generate_response
from app.vectorstore import semantic_search

PERSONAL_ELIGIBILITY_TERMS = (
    "am i eligible",
    "am i personally eligible",
    "am i eligible personally",
    "my eligibility",
    "personally eligible",
    "check my eligibility",
    "verify my eligibility",
    "verify whether i am eligible",
    "can you verify",
    "is my name in the beneficiary list",
)


def is_personal_eligibility_question(question: str) -> bool:
    normalized = " ".join(question.lower().split())

    return any(
        term in normalized
        for term in PERSONAL_ELIGIBILITY_TERMS
    )


def is_coverage_question(question: str) -> bool:
    question = question.lower()

    return (
        "coverage" in question
        or "cover" in question
        or "maximum amount" in question
        or "health insurance amount" in question
    )


def get_source_based_coverage_answer(retrieved: list) -> str | None:
    """
    Use a direct source-based answer when the retrieved text
    explicitly contains the PM-JAY annual coverage limit.
    """
    for item in retrieved:
        text = item.get("text", "").lower()

        has_coverage_limit = (
            "5,00,000" in text
            or "5 lakh" in text
            or "five lakh" in text
        )

        has_pmjay_context = (
            "pm-jay" in text
            or "ab pm-jay" in text
            or "beneficiary" in text
        )

        if has_coverage_limit and has_pmjay_context:
            return (
                "Under the AB PM-JAY scheme, eligible beneficiary "
                "families receive health coverage of up to ₹5,00,000 "
                "per family per year for covered hospitalisation."
            )

    return None


def build_citations(retrieved: list) -> list:
    citations = []

    for index, item in enumerate(retrieved, start=1):
        metadata = item.get("metadata") or {}

        citations.append({
            "citation_id": index,
            "chunk_id": item.get("chunk_id", ""),
            "document": metadata.get(
                "title", "Healthcare document"
            ),
            "page": metadata.get(
                "page", "Page not specified"
            ),
            "source": metadata.get("source", ""),
        })

    return citations


def ask_question(question: str, top_k: int = 5) -> dict:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    # Personal eligibility must never be inferred from general documents.
    if is_personal_eligibility_question(question):
        return {
            "question": question,
            "answer": (
                "I don't know. I cannot verify your personal PM-JAY "
                "eligibility because I do not have access to an "
                "authorised beneficiary-verification service. "
                "Please check through the official PM-JAY beneficiary "
                "portal or an authorised help centre."
            ),
            "citations": [],
            "retrieved_chunks": 0,
        }

    # Retrieve relevant document chunks.
    retrieved = semantic_search(
        query=question,
        n_results=top_k
    )

    if not retrieved:
        return {
            "question": question,
            "answer": (
                "I don't know. The available AyushmanSathi "
                "documents do not provide enough information."
            ),
            "citations": [],
            "retrieved_chunks": 0,
        }

    # Prepare source context and citations.
    context_parts = []

    for index, item in enumerate(retrieved, start=1):
        metadata = item.get("metadata") or {}

        context_parts.append(
            f"[{index}]\n"
            f"Document: {metadata.get('title', 'Healthcare document')}\n"
            f"Page: {metadata.get('page', 'Not specified')}\n"
            f"Content: {item.get('text', '')}"
        )

    context = "\n\n".join(context_parts)
    citations = build_citations(retrieved)

    # Direct source-based fallback for the explicitly documented
    # PM-JAY coverage limit.
    if is_coverage_question(question):
        coverage_answer = get_source_based_coverage_answer(retrieved)

        if coverage_answer:
            return {
                "question": question,
                "answer": coverage_answer + " [1]",
                "citations": citations[:1],
                "retrieved_chunks": len(retrieved),
            }

    prompt = f"""
You are AyushmanSathi, a healthcare information assistant.

Answer the user's question using the retrieved document excerpts.

IMPORTANT RULES:

1. Read all the retrieved excerpts carefully before answering.
2. The excerpts are the evidence. Do not ignore information that
   directly answers the question.
3. If an excerpt clearly contains the requested fact, answer using it.
4. Do not say "I don't know" when the answer is clearly present.
5. Do not use information outside the retrieved excerpts.
6. If the excerpts do not contain enough information, answer:
   "I don't know. The available documents do not provide enough information."
7. Add citation numbers such as [1] after factual statements.
8. Do not claim to verify anyone's personal PM-JAY eligibility.
9. Do not diagnose diseases or prescribe medicines.
10. Keep the answer clear and concise.

Example:
If the question asks for the maximum PM-JAY coverage and the excerpts
state ₹5,00,000 per family per year, answer with that amount.

USER QUESTION:
{question}

RETRIEVED DOCUMENT EXCERPTS:
{context}

Return ONLY valid JSON in this format:
{{
    "answer": "Your answer with citation numbers",
    "supported": true
}}

If the excerpts do not support an answer, set supported to false.
"""

    try:
        response = generate_response(prompt)

        cleaned = response.replace("```json", "").replace("```", "").strip()

        # Extract JSON if the model adds text around it.
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if not match:
            raise ValueError("Gemini did not return valid JSON.")

        result = json.loads(match.group())

        answer = str(result.get("answer", "")).strip()
        supported = result.get("supported", False)

        if not answer or not supported:
            return {
                "question": question,
                "answer": (
                    "I don't know. The available documents do not "
                    "provide enough information."
                ),
                "citations": [],
                "retrieved_chunks": 0,
            }

        # Keep only citations actually referenced in the answer.
        cited_ids = {
            int(value)
            for value in re.findall(r"\[(\d+)\]", answer)
        }

        used_citations = [
            citation
            for citation in citations
            if citation["citation_id"] in cited_ids
        ]

        if not used_citations:
            return {
                "question": question,
                "answer": (
                    "I don't know. The available documents do not "
                    "provide enough information."
                ),
                "citations": [],
                "retrieved_chunks": 0,
            }

        return {
            "question": question,
            "answer": answer,
            "citations": used_citations,
            "retrieved_chunks": len(retrieved),
        }

    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Could not process Gemini response: {e}") from e
    except Exception as e:
        raise RuntimeError(f"RAG answering failed: {e}") from e
