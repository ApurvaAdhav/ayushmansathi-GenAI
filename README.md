## 🏥 AyushmanSathi – AI-Powered Healthcare Assistant
## Project Overview

AyushmanSathi is a Generative AI-based healthcare assistant designed to make general healthcare information more accessible and understandable. It aims to provide users with a conversational interface where they can ask health-related questions and receive informative responses using trusted healthcare resources.

## Project Information

| Component | Description |
|---|---|
| Product Name | AyushmanSathi |
| Domain | Healthcare and Generative AI |
| Target Users | Patients, caregivers, and the general public |
| Problem Statement | Difficulty in accessing and understanding reliable healthcare information |
| Proposed Solution | A conversational AI assistant for answering general healthcare-related queries |
| Data Sources | World Health Organization (WHO), Ministry of Health and Family Welfare (MoHFW), and other verified public healthcare resources |

## Problem Statement

Accessing reliable healthcare information can be challenging due to scattered resources, complex medical terminology, and difficulty understanding health-related topics. Users need a simple and accessible way to explore general healthcare information.

## Proposed Solution

AyushmanSathi aims to provide a conversational AI platform that helps users explore healthcare information through natural language interactions. The system will focus on providing understandable responses based on trusted healthcare resources.

## How to Run the API

1. Activate the virtual environment:

```bash
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

4. Open Swagger UI in your browser:

```text
http://127.0.0.1:8000/docs
```

### Available API Endpoints

  `GET /health` – Check API status.
  `GET /records` – Get records with an optional limit.
  `GET /records/{id}` – Get a specific record.
  `GET /search?q=eligibility` – Search healthcare records.
  `POST /questions` – Submit a healthcare question.

## Project Development

Developing as part of the GenAI Training Program at Sanjivani.

**Repository:** ayushmansathi-genAI
