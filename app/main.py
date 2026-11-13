from fastapi import FastAPI, HTTPException
from app.records import load_records, get_by_id, search
from app.smart_search import smart_search
from app.llm import generate_response
from pydantic import BaseModel
from pathlib import Path
import json

# Request models
class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    task: str = "general"


# Response model
class ChatResponse(BaseModel):
    answer: str
    confidence: str
    follow_up: str


app = FastAPI(title="AyushmanSathi API")


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "AyushmanSathi API is running"
    }


# Get records with a limit
@app.get("/records")
def get_records(limit: int = 10):
    records = load_records()

    return {
        "total_records": len(records),
        "records": records[:limit]
    }


# Get a single record by ID
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


# Search healthcare records
@app.get("/search")
def search_records(q: str):
    results = smart_search(q)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# Ask a healthcare question
@app.post("/questions")
def ask_question(data: Question):
    records = load_records()
    results = search(records, data.question)

    return {
        "question": data.question,
        "total_results": len(results),
        "results": results
    }


# AI Chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest):

    # Select task prompt
    if data.task == "schemes":
        prompt_file = "task2.txt"
    else:
        prompt_file = "task1.txt"

    # Read prompt files
    prompt_dir = Path(__file__).resolve().parent.parent / "prompts"

    system_prompt = (prompt_dir / "system.txt").read_text(
        encoding="utf-8"
    )

    task_prompt = (prompt_dir / prompt_file).read_text(
        encoding="utf-8"
    )

    # Prepare complete prompt
    full_prompt = f"""
{system_prompt}

{task_prompt}

User Question: {data.question}

Return ONLY valid JSON in this format:
{{
    "answer": "Your answer here",
    "confidence": "High, Medium, or Low",
    "follow_up": "A relevant follow-up question"
}}
"""

    # Generate response using Gemini
    try:
        response = generate_response(full_prompt)

        # Clean response
        cleaned_response = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        # Convert response into JSON
        result = json.loads(cleaned_response)

        return ChatResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            follow_up=result["follow_up"]
        )

    except (json.JSONDecodeError, KeyError, TypeError):
        return ChatResponse(
            answer=response,
            confidence="Low",
            follow_up="Would you like to know more?"
        )