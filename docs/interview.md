
# AyushmanSathi – Interview Preparation

## 1. 60-Second Project Pitch

AyushmanSathi is an AI-powered healthcare information assistant designed to make healthcare scheme information easier to access and understand.

The main problem I focused on is that healthcare policy manuals are lengthy and contain complex rules, procedure codes, and annexures. Finding the correct information and providing reliable answers with citations can be challenging.

I developed AyushmanSathi using Python, FastAPI, Streamlit, Google Gemini, ChromaDB, Sentence Transformers, and LangGraph.

It uses a Retrieval-Augmented Generation pipeline to retrieve relevant information from healthcare documents and generate context-based answers with citations. It also includes smart search, a healthcare coverage balance tracker, and a human approval workflow.

One of my biggest challenges was handling differences between HBP 2.0 and HBP 2.2 while preserving exact section and page references.

The goal of AyushmanSathi is to make healthcare information more accessible, understandable, and easier to verify.

---

## 2. Ten Likely Interview Questions and Answers

### Q1. What is AyushmanSathi?

AyushmanSathi is a Generative AI-powered healthcare information assistant. It helps users find information from healthcare documents and provides context-based answers with citations. It also supports healthcare coverage tracking and an AI agent workflow.

### Q2. What problem does your project solve?

Healthcare manuals are lengthy and contain technical terms, procedure codes, eligibility rules, and annexures. Users may find it difficult to locate the correct information. AyushmanSathi simplifies this process by retrieving relevant information and presenting it in a conversational format.

### Q3. Why did you use RAG instead of a normal chatbot?

A normal chatbot generates answers mainly from its trained knowledge and may not know the latest information in a specific healthcare manual. RAG retrieves relevant information from the project's document collection and provides it as context to the language model. This helps generate more relevant and verifiable answers.

### Q4. Explain the architecture of AyushmanSathi.

The project has a Streamlit frontend and a FastAPI backend. The backend processes user requests and uses different components depending on the request.

The RAG pipeline retrieves relevant document content using embeddings and ChromaDB. Gemini generates the final response using the retrieved context. LangGraph manages the agent workflow and its tools.

### Q5. What was the hardest technical challenge you faced?

One of the hardest challenges was retrieving accurate information from lengthy healthcare manuals.

The manuals contain procedure codes such as ER003A and MO010C, multiple annexures, and rules that can differ between HBP 2.0 and HBP 2.2.

A search result may look relevant but still come from an older manual. Therefore, retrieval needs to prioritize the newer HBP 2.2 version when applicable. I also needed to preserve document version, section, and page metadata so that citations point to the exact source.

This taught me that accurate retrieval is not just about finding similar text; it is also about understanding document versions and preserving source information.

### Q6. How does your RAG pipeline work?

The pipeline follows these steps:

1. Load healthcare PDF documents.
2. Extract and clean the text.
3. Divide the text into smaller chunks.
4. Generate embeddings using Sentence Transformers.
5. Store the embeddings in ChromaDB.
6. Retrieve relevant chunks for a user's question.
7. Send the retrieved context to Gemini.
8. Generate an answer with source citations.

### Q7. What is ChromaDB, and why did you use it?

ChromaDB is a vector database used to store and retrieve text embeddings. I used it to store healthcare document chunks and perform similarity-based retrieval. It helps find information based on the meaning of a question rather than relying only on exact keyword matches.

### Q8. What is LangGraph, and how is it used in your project?

LangGraph is a framework for building stateful AI agent workflows. In AyushmanSathi, it helps coordinate the agent's tools, including RAG search and the healthcare coverage balance tracker. It also supports a human-in-the-loop approval workflow for package-related decisions.

### Q9. How did you test and improve your application?

I used pytest for automated testing and Ruff for code-quality checks. I also evaluated two retrieval configurations using 15 healthcare-related questions. The selected configuration had a higher average keyword score. For production readiness, I added response caching, input validation, and latency and token logging.

### Q10. How did you deploy your project?

I used Docker to package the application and GitHub Actions for continuous integration. The FastAPI backend is deployed on Render. I verified the public health endpoint to confirm that the deployed API was running successfully.

---

## 3. Key Technical Points to Remember

| Topic | Answer |
|---|---|
| Project | AyushmanSathi |
| Domain | Healthcare and Generative AI |
| Backend | FastAPI |
| Frontend | Streamlit |
| LLM | Google Gemini |
| RAG database | ChromaDB |
| Embeddings | Sentence Transformers |
| Agent framework | LangGraph |
| Testing | Pytest |
| Code quality | Ruff |
| Deployment | Render |
| Containerization | Docker |
| CI | GitHub Actions |

## 4. Interview Tips

- Explain the problem before explaining the technologies.
- Be ready to explain the complete RAG pipeline.
- Clearly explain why document versioning matters.
- Use ER003A and MO010C as examples when discussing retrieval challenges.
- Explain how section and page metadata help make citations traceable.
- Do not claim that AI provides medical diagnoses. AyushmanSathi is a healthcare information assistant.
- Be honest about limitations and distinguish implemented features from future improvements.
