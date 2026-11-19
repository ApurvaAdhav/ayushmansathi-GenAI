
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.graph import agent_graph
from app.llm import generate_response
from app.rag import ask_question as rag_ask_question
from app.records import get_by_id, load_records, search
from app.smart_search import smart_search
from app.vectorstore import semantic_search

# -----------------------------
# Project Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_DIR = BASE_DIR / "prompts"


# -----------------------------
# Request and Response Models
# -----------------------------

class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    task: str = "task1"


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    follow_up: str


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class AgentRequest(BaseModel):
    message: str = ""
    thread_id: str = "default"
    approval: bool | None = None


# -----------------------------
# Initialize FastAPI
# -----------------------------

app = FastAPI(title="AyushmanSathi API")


# -----------------------------
# 1. Health Check
# -----------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "AyushmanSathi API is running"
    }


# -----------------------------
# 2. Get All Records
# -----------------------------

@app.get("/records")
def get_records(limit: int = 10):
    records = load_records()

    return {
        "total_records": len(records),
        "records": records[:limit]
    }


# -----------------------------
# 3. Get Record by ID
# -----------------------------

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


# -----------------------------
# 4. Keyword / TF-IDF Search
# -----------------------------

@app.get("/search")
def search_records(q: str):
    results = smart_search(q)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# -----------------------------
# 5. Semantic Search using ChromaDB
# -----------------------------

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


# -----------------------------
# 6. Search Healthcare Questions
# -----------------------------

@app.post("/questions")
def search_questions(data: Question):
    records = load_records()
    results = search(records, data.question)

    return {
        "question": data.question,
        "total_results": len(results),
        "results": results
    }


# -----------------------------
# 7. Chat with Gemini
# -----------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest):

    if data.task not in ["task1", "task2"]:
        raise HTTPException(
            status_code=400,
            detail="Task must be task1 or task2"
        )

    try:
        system_prompt = (PROMPT_DIR / "system.txt").read_text(
            encoding="utf-8"
        )

        task_prompt = (PROMPT_DIR / f"{data.task}.txt").read_text(
            encoding="utf-8"
        )

        records = smart_search(data.question)

        context = "\n\n".join(
            record["rule_topic"] + "\n" + record["rule_text"]
            for record in records
        )

        if not context:
            context = "No relevant healthcare information was found."

        formatted_task = (
            task_prompt
            .replace("{question}", data.question)
            .replace("{context}", context)
        )

        full_prompt = f"""
{system_prompt}

{formatted_task}

Return only valid JSON:
{{
    "answer": "Your answer",
    "confidence": 0.0,
    "follow_up": "Your follow-up question"
}}
"""

        response = generate_response(full_prompt)

        cleaned_response = (
            response.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(cleaned_response)

        return ChatResponse(
            answer=result["answer"],
            confidence=float(result["confidence"]),
            follow_up=result["follow_up"]
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


# -----------------------------
# 8. RAG Question Answering
# -----------------------------

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


# -----------------------------
# 9. LangGraph Agent
# -----------------------------

@app.post("/agent")
def run_langgraph_agent(data: AgentRequest):

    config = {
        "configurable": {
            "thread_id": data.thread_id
        }
    }

    try:

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
