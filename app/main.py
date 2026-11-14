from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.records import load_records, get_by_id, search
from app.smart_search import smart_search
from app.llm import generate_response
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_DIR = BASE_DIR / "prompts"


class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    task: str = "task1"


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    follow_up: str


app = FastAPI(title="AyushmanSathi API")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "AyushmanSathi API is running"
    }


@app.get("/records")
def get_records(limit: int = 10):
    records = load_records()
    return {
        "total_records": len(records),
        "records": records[:limit]
    }


@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()
    record = get_by_id(records, record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return record


@app.get("/search")
def search_records(q: str):
    results = smart_search(q)
    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


@app.post("/questions")
def ask_question(data: Question):
    records = load_records()
    results = search(records, data.question)

    return {
        "question": data.question,
        "total_results": len(results),
        "results": results
    }


@app.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest):

    if data.task not in ["task1", "task2"]:
        raise HTTPException(
            status_code=400,
            detail="Task must be task1 or task2"
        )

    # Load system and task prompts
    system_prompt = (PROMPT_DIR / "system.txt").read_text(
        encoding="utf-8"
    )

    task_prompt = (PROMPT_DIR / f"{data.task}.txt").read_text(
        encoding="utf-8"
    )

    # Retrieve relevant healthcare records
    records = smart_search(data.question)

    context = "\n\n".join(
        record["rule_topic"] + "\n" + record["rule_text"]
        for record in records
    )

    if not context:
        context = "No relevant healthcare information was found."

    # Insert question and context into task prompt
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

    try:
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

    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid response format"
        )

    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
