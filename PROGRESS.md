# AyushmanSathi – Project Progress

## Day 1: Project Setup

- [x] Created public GitHub repo `sanjivani-sj-30-ayushmansathi` and cloned it.
- [x] Wrote `README.md` with project card (product, user, problem, data source).
- [x] Created `day01_intro.py` — prints project card using variables and f-strings, asks user name and question with `input()`.
- [x] Created `day01_menu.py` — while-loop menu with 4 options (about, sample questions, rule check, exit).
- [x] Pushed to GitHub.

## Day 2: Data Collection

- [x] Hand-collected 20 PM-JAY rules covering cover amount, eligibility, beneficiary identification, pre-authorisation, discharge against advice, death in hospital, referrals, unspecified packages, 5 Annexure 1 exclusions, and 5 Section 5 FAQs.
- [x] Stored rules as list of dicts in `data/sample_records.py` with fields: `rule_topic`, `rule_text`, `applies_to`, `document_title`, `page_or_section`, `source_url`.
- [x] Implemented print-all, search-by-keyword, and count-per-category functions.
- [x] Refactored into `app/records.py` (`load_records`, `search`, `count_by`, `get_by_id`) and `app/cli.py`.
- [x] Added `.venv`, `requirements.txt`, and `.gitignore`.

## Day 3: Data Ingestion

- [x] Downloaded HBP 2.2 manual and Beneficiary Identification Guidelines into `data/raw/`.
- [x] Created `app/ingest.py` — extracts text from PDFs, cleans it into the standard fields, handles bad rows with `try/except`, saves to `data/records.json`.
- [x] Created `app/models.py` — `Record` dataclass.
- [x] Created `app/fetch.py` — downloads 3+ documents with `requests`, timeouts, and error handling.

## Day 4: FastAPI Backend

- [x] Created `app/main.py` with FastAPI service.
- [x] Endpoints: `GET /health`, `GET /records?limit=`, `GET /records/{id}` (404 if missing), `GET /search?q=`, `POST /questions`.
- [x] Added `README` section: **How to Run**.
- [x] Created `analysis/explore.py` — prints 3 facts about records using pandas.
- [x] Created `app/smart_search.py` — TF-IDF + cosine similarity ranking powering `GET /search`.
- [x] Tagged `week-1`.

## Day 5: LLM Concepts + Checkpoint 1

- [x] Created `docs/how_llms_work.md` — explains LLMs in own words with 1 diagram.
- [x] Added 10 real AyushmanSathi user questions (Q6 is unanswerable from available data).
- [x] Verified FastAPI `/docs` page loads correctly.
- [x] Tagged `checkpoint-1` (tagged as `day-5-checkpoint-1`).

## Day 6: LLM Integration

- [x] Created `app/llm.py` — Gemini provider wrapper.
- [x] Added `POST /chat` endpoint with AyushmanSathi system prompt.
- [x] `.env` is not committed; `.env.example` is committed.
- [x] Created `prompts/` folder with `system.txt`, `task1.txt`, `task2.txt`.
- [x] `/chat` returns JSON: `answer`, `confidence`, `follow_up`.
- [x] Created `eval/prompt_compare.md` — compares 2 prompt versions on 10 questions.

## Day 7: Chunking and Embeddings

- [x] Created `app/chunking.py` — chunks documents keeping source, page, and title metadata.
- [x] Created `app/embed.py` — generates embeddings with `all-MiniLM-L6-v2`.
- [x] Created `app/vectorstore.py` — indexes all chunks into a persistent ChromaDB collection (181 chunks).
- [x] Added `GET /search/semantic?q=` endpoint.
- [x] Recorded semantic search results in `eval/search_results.md`.

## Day 8: RAG Pipeline

- [x] Created `app/rag.py` — retrieves chunks and generates answers with citations.
- [x] Added `POST /ask` endpoint.
- [x] Returns "I don't know" for Q6 (personal eligibility).
- [x] Created `eval/eval_set.json` — 15 evaluation rows.
- [x] Created `eval/run_eval.py` — runs 2 configurations (chunk size / top-k).
- [x] Configuration B (chunk 1000, top-k 5) won with average keyword score 0.5444 vs 0.3929.
- [x] Winner table added to README.

## Day 9: Agent Tools

- [x] Created `app/tools.py` — `cover_balance_tracker` tool.
- [x] Created `app/agent_loop.py` — hand-written agent calling RAG search and the cover tool.
- [x] Created `app/graph.py` — LangGraph agent with memory and one human-approval step.
- [x] Added `POST /agent` endpoint.

## Day 10: Streamlit UI — Checkpoint 2

- [x] Created `ui/app.py` — Streamlit chat calling `/ask` or `/agent`.
- [x] Shows citations on every answer.
- [x] Saves thumbs-up / thumbs-down feedback to `ui/feedback.json`.
- [x] Signature feature: **Covered / Not covered / Needs pre-approval** badge on every answer.
- [x] Screenshot added to README.
- [x] Tagged `checkpoint-2`.

## Day 11: Tests and Docker

- [x] Created `tests/` with 20 pytest tests (records, search, `/health`, `/ask` with fake LLM, agent tool).
- [x] `ruff check .` passes.
- [x] Created `Dockerfile`, `.dockerignore`, and `docker-compose.yml`.
- [x] Added **Run with Docker** section to README.

## Day 12: CI/CD and Deployment

- [x] Created `.github/workflows/ci.yml` — ruff, pytest, docker build steps.
- [x] Green CI badge in README.
- [x] Merged at least 1 PR from a feature branch after CI passed.
- [x] Deployed AyushmanSathi to Render.
- [x] Live URL: `https://ayushmansathi-api.onrender.com`
- [x] `/health` works publicly.

## Day 13: Production Hardening

- [x] Logs latency and tokens per request.
- [x] LRU cache with capacity 100.
- [x] Input length limit: 1,000 characters.
- [x] Prompt-injection test documented.
- [x] README: **Production Notes** section with observed numbers.
- [x] README: Mermaid architecture diagram.
- [x] README: Results table.
- [x] Created `docs/resume.md` with 3 resume bullets.

## Day 14: Interview Preparation

- [x] Created `docs/interview.md` with 60-second pitch and answers to 10 likely interview questions.
- [x] Documented the hardest technical problem (HBP version preference, section/page metadata for exact citations).
- [x] Rehearsed demo twice.
- [x] Fixed 3 root-cause RAG bugs (prompt placeholder leak, citation-stripping, `format()` crash on JSON braces).
- [ ] Create and push `final` git tag.

## Open Items

- Push `final` tag after the last verification pass.
- Add demo video link to README once recording is available.

## Technical Challenge (Interview Story)

The hardest problem was retrieving accurate answers from long healthcare manuals containing procedure codes (ER003A, MO010C), annexures, and rules that differ between HBP 2.0 and HBP 2.2.

The solution:
- Version metadata (`version` field) is extracted from every chunk at ingest time.
- `vectorstore.py` applies a small version-preference bonus during re-ranking so HBP 2.2 chunks score slightly higher than HBP 2.0 chunks at equal semantic distance.
- Section and page metadata are preserved in ChromaDB so citations include exact references.
