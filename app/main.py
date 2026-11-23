import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.records import get_by_id, load_records, search
from app.smart_search import smart_search

# Project Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_DIR = BASE_DIR / "prompts"


# Request and Response Models
class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    task: str = "task1"


class Citation(BaseModel):
    citation_id: int
    chunk_id: str
    document: str
    page: str
    section: str = "Section not specified"
    version: str = "Unknown"
    source: str


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    follow_up: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved_chunks: int = 0


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class AgentRequest(BaseModel):
    message: str = ""
    thread_id: str = "default"
    approval: bool | None = None


# Initialize FastAPI
app = FastAPI(title="AyushmanSathi API")


# Lazy-loading wrapper for RAG
def rag_ask_question(question, top_k=5):
    from app.rag import ask_question

    return ask_question(
        question=question,
        top_k=top_k
    )


# Build citations from retrieved chunks
def build_chat_citations(retrieved: list) -> list:
    citations = []

    for index, item in enumerate(retrieved, start=1):
        metadata = item.get("metadata") or {}

        citations.append({
            "citation_id": index,
            "chunk_id": item.get("chunk_id", ""),
            "document": metadata.get(
                "title", "Healthcare document"
            ),
            "page": str(metadata.get(
                "page", "Page not specified"
            )),
            "section": str(metadata.get(
                "section", "Section not specified"
            )),
            "version": str(metadata.get(
                "version", "Unknown"
            )),
            "source": metadata.get("source", "")
        })

    return citations


# Extract individual citation numbers,
# including grouped citations such as [2, 3]
def extract_citation_ids(answer: str) -> set[int]:
    cited_ids = set()

    citation_groups = re.findall(
        r"\[(\d+(?:\s*,\s*\d+)*)\]",
        answer
    )

    for group in citation_groups:
        for value in group.split(","):
            cited_ids.add(int(value.strip()))

    return cited_ids


# 1. Health Check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "AyushmanSathi API is running"
    }


# 2. Get All Records
@app.get("/records")
def get_records(limit: int = 10):
    records = load_records()

    return {
        "total_records": len(records),
        "records": records[:limit]
    }


# 3. Get Record by ID
@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()
    record = get_by_id(records, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    return record


# 4. Keyword / TF-IDF Search
@app.get("/search")
def search_records(q: str):
    results = smart_search(q)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# 5. Semantic Search using ChromaDB
@app.get("/search/semantic")
def search_semantic(q: str, limit: int = 5):

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 20"
        )

    try:
        from app.vectorstore import semantic_search

        results = semantic_search(
            query=q,
            n_results=limit
        )

        return {
            "query": q,
            "total_results": len(results),
            "results": results
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {e!s}"
        ) from e


# 6. Search Healthcare Questions
@app.post("/questions")
def search_questions(data: Question):
    records = load_records()
    results = search(records, data.question)

    return {
        "question": data.question,
        "total_results": len(results),
        "results": results
    }


# 7. Chat with Gemini and Source Citations
@app.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest):

    if data.task not in ["task1", "task2"]:
        raise HTTPException(
            status_code=400,
            detail="Task must be task1 or task2"
        )

    try:
        from app.llm import generate_response
        from app.vectorstore import semantic_search

        # Load prompts
        system_prompt = (PROMPT_DIR / "system.txt").read_text(
            encoding="utf-8"
        )

        task_prompt = (PROMPT_DIR / f"{data.task}.txt").read_text(
            encoding="utf-8"
        )

        # Retrieve relevant chunks from ChromaDB
        retrieved = semantic_search(
            query=data.question,
            n_results=5
        )

        # Build citations from the same retrieved chunks
        citations = build_chat_citations(retrieved)

        # Prepare context with citation numbers and metadata
        context_parts = []

        for index, item in enumerate(retrieved, start=1):
            metadata = item.get("metadata") or {}

            context_parts.append(
                f"[{index}]\n"
                f"Document: {metadata.get('title', 'Healthcare document')}\n"
                f"Version: {metadata.get('version', 'Unknown')}\n"
                f"Section: {metadata.get('section', 'Section not specified')}\n"
                f"Page: {metadata.get('page', 'Not specified')}\n"
                f"Content: {item.get('text', '')}"
            )

        context = "\n\n".join(context_parts)

        if not context:
            context = "No relevant healthcare information was found."

        # Format task prompt
        formatted_task = (
            task_prompt
            .replace("{question}", data.question)
            .replace("{context}", context)
        )

        full_prompt = f"""
{system_prompt}

{formatted_task}

IMPORTANT CITATION RULES:

1. Answer using only the retrieved document excerpts.
2. Add citation numbers such as [1] after factual statements.
3. Multiple citations may be grouped as [1, 2].
4. Use only citation numbers provided in the retrieved excerpts.
5. Do not invent document names, page numbers, sections, versions, or sources.
6. If the excerpts do not contain enough information, clearly say so.
7. Do not claim to verify personal PM-JAY eligibility.

Return only valid JSON:

{{
    "answer": "Your answer with citation numbers",
    "confidence": 0.0,
    "follow_up": "Your follow-up question"
}}
"""

        # Generate response
        response = generate_response(full_prompt)

        cleaned_response = (
            response.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(cleaned_response)

        answer = str(result["answer"]).strip()
        confidence = float(result["confidence"])
        follow_up = str(result["follow_up"]).strip()

        # Validate confidence
        if not 0 <= confidence <= 1:
            raise ValueError(
                "Confidence must be between 0 and 1."
            )

        # Extract all citation numbers from the answer
        cited_ids = extract_citation_ids(answer)

        # Return only citations actually referenced in the answer.
        # If the LLM gave a real answer but forgot citation markers,
        # attach all retrieved citations rather than returning none.
        used_citations = [
            citation
            for citation in citations
            if citation["citation_id"] in cited_ids
        ]

        answer_lower = answer.lower()
        answer_says_dont_know = (
            "i don't know" in answer_lower
            or "i do not know" in answer_lower
            or "not provide enough information" in answer_lower
        )

        if not used_citations and answer and not answer_says_dont_know:
            used_citations = citations

        return ChatResponse(
            answer=answer,
            confidence=confidence,
            follow_up=follow_up,
            citations=used_citations,
            retrieved_chunks=len(retrieved)
        )

    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid response format"
        ) from e

    except RuntimeError as e:
        raise HTTPException(
            status_code=502,
            detail=str(e)
        ) from e


# 8. RAG Question Answering
@app.post("/ask")
def ask(data: AskRequest):

    if not data.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        result = rag_ask_question(
            question=data.question,
            top_k=data.top_k
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e

    except RuntimeError as e:
        raise HTTPException(
            status_code=502,
            detail=str(e)
        ) from e


# 9. LangGraph Agent
@app.post("/agent")
def run_langgraph_agent(data: AgentRequest):

    try:
        from langgraph.types import Command

        from app.graph import agent_graph

        config = {
            "configurable": {
                "thread_id": data.thread_id
            }
        }

        # Resume an interrupted agent after approval/rejection
        if data.approval is not None:
            result = agent_graph.invoke(
                Command(
                    resume={"approved": data.approval}
                ),
                config=config
            )

        # Start a new agent request
        else:
            if not data.message.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Message cannot be empty"
                )

            result = agent_graph.invoke(
                {"message": data.message},
                config=config
            )

        # Check whether human approval is required
        if "__interrupt__" in result:
            pending = result["__interrupt__"][0]

            return {
                "status": "approval_required",
                "thread_id": data.thread_id,
                "approval_request": pending.value
            }

        # Return completed agent response
        return {
            "status": "completed",
            "thread_id": data.thread_id,
            "tool_used": result.get("tool_used"),
            "result": result.get("result"),
            "citations": result.get("citations", []),
            "approval_status": result.get("approval_status"),
            "answer": result.get("answer")
        }

    except HTTPException:
        raise

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {e!s}"
        ) from e
