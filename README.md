# 🏥 AyushmanSathi – AI-Powered Healthcare Assistant

## Project Overview

AyushmanSathi is a Generative AI-based healthcare assistant designed to make general healthcare information more accessible and understandable. It provides a conversational interface where users can ask healthcare-related questions and receive informative, context-based responses using trusted healthcare documents.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from healthcare documents and generate responses using a Large Language Model (LLM).

## Project Information

| Component | Description |
|---|---|
| Product Name | AyushmanSathi |
| Domain | Healthcare and Generative AI |
| Target Users | Patients, caregivers, and the general public |
| Problem Statement | Difficulty in accessing and understanding reliable healthcare information |
| Proposed Solution | A conversational AI assistant for answering healthcare-related queries |
| Data Sources | WHO, Ministry of Health and Family Welfare (MoHFW), and other verified public healthcare resources |

## Problem Statement

Accessing reliable healthcare information can be challenging due to scattered resources, complex medical terminology, and difficulty understanding health-related topics. Users need a simple and accessible way to explore general healthcare information.

## Proposed Solution

AyushmanSathi provides a conversational AI platform that allows users to explore healthcare information through natural language interactions. It retrieves relevant information from trusted healthcare documents and uses Generative AI to provide understandable, context-based answers with source citations.

## Key Features

- Healthcare document extraction and processing.
- Text chunking with configurable chunk size and overlap.
- Text embeddings for semantic representation.
- ChromaDB for vector storage and similarity-based retrieval.
- Retrieval-Augmented Generation (RAG) pipeline.
- Gemini API integration for AI-generated responses.
- Context-based question answering with source citations.
- Semantic search using vector embeddings.
- Keyword-based healthcare record search.
- Smart search using TF-IDF and cosine similarity.
- FastAPI-based REST API.
- Safe fallback response for questions requiring personal eligibility verification.
- Interactive API documentation through Swagger UI.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Generative AI | Google Gemini API |
| RAG Framework | Custom RAG Pipeline |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers |
| Document Processing | PyPDF |
| Machine Learning | TF-IDF, Cosine Similarity |
| API Testing | Swagger UI |
| Version Control | Git and GitHub |

## How to Run the API

### 1. Clone the repository

```bash
git clone https://github.com/ApurvaAdhav/ayushmansathi-GenAI.git
cd ayushmansathi-GenAI
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key
```

Keep your `.env` file private and do not commit it to GitHub.

### 5. Start the FastAPI server

```bash
python -m uvicorn app.main:app --reload
```

### 6. Open Swagger UI

Visit:

http://127.0.0.1:8000/docs

## Available API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API status |
| GET | `/records` | Retrieve healthcare records |
| GET | `/records/{record_id}` | Retrieve a specific record |
| GET | `/search` | Search healthcare records |
| GET | `/search/semantic` | Perform semantic search |
| POST | `/questions` | Submit a healthcare question |
| POST | `/chat` | Interact with the AI assistant |
| POST | `/ask` | Ask questions using the RAG pipeline |

## RAG Pipeline

The Retrieval-Augmented Generation pipeline follows these steps:

1. Document Loading – Load healthcare documents.
2. Text Processing – Extract and clean document content.
3. Chunking – Divide documents into smaller text segments.
4. Embedding Generation – Convert chunks into vector representations.
5. Vector Storage – Store embeddings in ChromaDB.
6. Semantic Retrieval – Retrieve relevant chunks based on user queries.
7. Context Preparation – Pass retrieved information to the LLM.
8. Response Generation – Generate context-based answers with citations.

## Evaluation and Configuration Comparison

Two configurations were evaluated using a dataset of 15 healthcare-related questions.

| Metric | Configuration A | Configuration B |
|---|---:|---:|
| Chunk Size | 500 | 1000 |
| Chunk Overlap | 150 | 150 |
| Top-K | 3 | 5 |
| Average Keyword Score | 0.3929 | 0.5444 |
| Scored Questions | 15 | 15 |
| Citation Availability Rate | 100% | 100% |

### Selected Configuration

Configuration B achieved a higher average keyword score and was selected as the preferred retrieval configuration.

- Chunk Size: 1000
- Chunk Overlap: 150
- Top-K: 5

*Note: Keyword score measures expected-term coverage in retrieved chunks. Citation availability does not independently establish citation correctness.*

## Project Structure

```text
ayushmansathi-GenAI/
│
├── analysis/
│   └── explore.py
│
├── app/
│   ├── main.py
│   ├── records.py
│   ├── models.py
│   ├── ingest.py
│   ├── fetch.py
│   ├── smart_search.py
│   ├── chunking.py
│   ├── embed.py
│   ├── vectorstore.py
│   ├── llm.py
│   └── rag.py
│
├── data/
│   ├── raw/
│   ├── records.json
│   ├── sample_records.py
│   └── chroma_db/
│
├── prompts/
│
├── eval/
│   ├── eval_set.json
│   ├── run_eval.py
│   ├── run_comparison.py
│   ├── prompt_compare.md
│   └── config_results.json
│
├── day01_intro.py
├── day01_menu.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Current Development Status

The project currently includes:

- Healthcare document ingestion and processing.
- Structured healthcare record management.
- Keyword-based and semantic search.
- Vector embeddings and ChromaDB integration.
- Gemini API integration.
- Retrieval-Augmented Generation implementation.
- FastAPI endpoints for healthcare queries and AI interactions.
- Context-based responses with source citations.
- Evaluation of two chunking and retrieval configurations.

## Future Scope

- Expand the healthcare knowledge base with additional verified documents.
- Improve retrieval accuracy and answer evaluation.
- Enhance response quality and citation verification.
- Add multilingual healthcare information support.
- Improve the conversational user interface.

## Project Development

Developed as part of the GenAI Training Program at Sanjivani.

## Repository

[AyushmanSathi – GitHub Repository](https://github.com/ApurvaAdhav/ayushmansathi-GenAI)
