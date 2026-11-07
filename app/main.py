from fastapi import FastAPI, HTTPException
from app.records import load_records, get_by_id, search
from app.smart_search import smart_search
from pydantic import BaseModel

class Question(BaseModel):
    question: str

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