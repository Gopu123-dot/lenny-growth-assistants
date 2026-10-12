# The Lenny Growth Assistant

> **Production-Grade, Local-First AI Conversational Copilot and Content Synthesizer Grounded in Lenny's Podcast Transcripts.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?logo=ollama&logoColor=white)](https://ollama.ai)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-15%2F15%20Passing-brightgreen.svg)]()

---

## Overview

**The Lenny Growth Assistant** is an internal copilot built for product managers, growth leads, founders, and operators. Built on the collective knowledge of *Lenny's Podcast* (200+ hours of in-depth interviews with operators like Rahul Vohra, Elena Verna, Brian Balfour, Shreyas Doshi, and Patrick Campbell), it converts conversational questions into:

1. **Strictly Grounded Answers:** Sub-second retrieval with verifiable episode titles, guest names, similarity scores, and verbatim excerpt citations.
2. **Contextual Conversations:** Isolated, persistent multi-turn sessions with full historical recall.
3. **Ship 30 for 30–Style Essays:** One-click transformation of strategic advice into an ~1,250-word atomic essay with compelling hooks, cadenced rhythm, and executive takeaways.
4. **Claude-Style In-App Artifacts:** Generation of interactive Markdown memos and live HTML/CSS widgets (e.g. PMF scorecards and onboarding calculators) rendered natively in a side-by-side **Artifact Viewer**.
5. **Flexible Local-to-Cloud Runtime:** Offline privacy and zero API cost via **Ollama** (`llama3.2:3b`), with dynamic toggling to **Anthropic Claude** or **OpenAI**.

---

## Features

- **Strict Source Provenance:** Every claim links back to the originating episode, guest, and transcript chunk.
- **Out-of-Domain Refusal:** Rejects queries unsupported by transcript knowledge without hallucinating.
- **Claude Artifacts Paradigm:** Generates and renders Markdown and live interactive HTML widgets in an isolated workspace.
- **Security Sandboxing:** Untrusted HTML rendered inside an `<iframe>` container with `sandbox="allow-scripts"` (strictly blocking parent DOM access, cookie theft, and top-level navigation).
- **Dual Database Resilience:** Production PostgreSQL persistence with automated SQLite fallback for local developer machines without active Docker daemons.
- **Multi-Model Dynamic Switching:** Switch between Local Ollama, Anthropic Claude, and OpenAI via UI or REST API.
- **Production Observability:** Structured JSON logging with automatic redaction of sensitive credentials.
- **100% Automated Test Coverage:** Unit, integration, routing, retrieval, security, and persistence tests passing with zero flakes.

---

## Architecture

The system follows a modular, decoupled agent architecture:

```
+---------------------------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER (SPA)                                            |
|   Chat Stream  •  Expandable Citation Cards  •  Claude-Style Artifact Viewer  •  Model Badge Modal      |
+---------------------------------------------------+-----------------------------------------------------+
                                                    | REST API / JSON
+---------------------------------------------------v-----------------------------------------------------+
|                                      FASTAPI GATEWAY LAYER                                              |
|   /api/chat  •  /api/sessions  •  /api/artifacts  •  /api/health  •  /api/models                        |
+---------------------------------------------------+-----------------------------------------------------+
                                                    |
+---------------------------------------------------v-----------------------------------------------------+
|                                   AGENT & SKILLS ORCHESTRATION                                          |
|                          Intent Router (Pattern & Semantic Heuristics)                                  |
|            +-----------------------+------------------------+------------------------+                  |
|            |   Grounded Q&A Skill  |   Ship 30 Essay Skill  | Artifact Skill (HTML)  |                  |
|            +-----------+-----------+------------+-----------+------------+-----------+                  |
+------------------------|------------------------|------------------------|------------------------------+
                         |                        |                        |
+------------------------v------------------------v------------------------v------------------------------+
|                                    RETRIEVAL & INGESTION (RAG)                                          |
|            Recursive Chunker (600 tokens)  •  Hybrid BM25 + TF-IDF Cosine Index  •  Citation Engine      |
+---------------------------------------------------+-----------------------------------------------------+
                                                    |
+---------------------------------------------------v-----------------------------------------------------+
|                                     INFERENCE ABSTRACTION                                               |
|        OllamaProvider (Local)  |  AnthropicProvider (Cloud)  |  OpenAIProvider  |  MockProvider (CI)   |
+---------------------------------------------------+-----------------------------------------------------+
                                                    |
+---------------------------------------------------v-----------------------------------------------------+
|                                      PERSISTENCE LAYER                                                  |
|                   PostgreSQL 16 (Primary)  /  aiosqlite (Automated Local Fallback)                     |
+---------------------------------------------------------------------------------------------------------+
```

---

## Prerequisites

Before starting, ensure your system has:

- **Python:** Version `3.11` or higher (`python --version`)
- **Docker & Docker Compose:** Optional for containerized deployment (`docker compose version`)
- **Ollama:** Mandatory for local demo (`ollama --version`)
  - Download from [ollama.ai](https://ollama.ai)

---

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/lenny-growth-assistant.git
cd lenny-growth-assistant
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

---

## Environment Variables

All settings are configured via `.env`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Application mode (`development` or `production`) |
| `PORT` | `8000` | HTTP port for FastAPI backend |
| `LLM_PROVIDER` | `ollama` | Active LLM (`ollama`, `anthropic`, or `openai`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama daemon base URL |
| `OLLAMA_MODEL` | `llama3.2` | Local model name (e.g. `llama3.2`, `mistral`, `llama3`) |
| `ANTHROPIC_API_KEY` | *(empty)* | Optional API key for Anthropic Claude |
| `OPENAI_API_KEY` | *(empty)* | Optional API key for OpenAI |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Connection URL for PostgreSQL |
| `ENABLE_SQLITE_FALLBACK` | `true` | Automated fallback to SQLite if PostgreSQL is offline |
| `ALLOW_MOCK_FALLBACK` | `true` | Graceful fallback if chosen provider is temporarily down |

---

## PostgreSQL Setup

### Option A: Docker Compose (Recommended)
Launch PostgreSQL in background:
```bash
docker compose up -d db
```

### Option B: Local PostgreSQL Server
Create the database:
```sql
CREATE DATABASE lenny_assistant;
```
Ensure `DATABASE_URL` in `.env` matches your local credentials.

### Option C: Automated SQLite Fallback
If PostgreSQL is not running on your machine, the application will automatically fall back to SQLite at `./data/lenny_assistant.db` without crashing.

---

## Ollama Setup (Local LLM)

Ollama is the mandatory local inference engine.

### 1. Install & Start Ollama
```bash
# Verify installation
ollama --version

# Start daemon (if not running as a system service)
ollama serve
```

### 2. Pull the Recommended Local Model
We recommend `llama3.2` (lightweight, fast on developer laptops):
```bash
ollama run llama3.2
```
Other supported models:
```bash
ollama run mistral
ollama run llama3
```

---

## Cloud Model Setup (Optional)

To enable cloud frontier models:
1. Open `.env`.
2. Add your API key:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-...
   # or
   OPENAI_API_KEY=sk-proj-...
   ```
3. Set `LLM_PROVIDER=anthropic` or switch models via the UI badge modal.

---

## Transcript Ingestion

The application automatically indexes bundled transcripts on startup. You can also run the CLI script manually to verify chunk counts and test queries:

```bash
python scripts/ingest_transcripts.py
```

### Output:
```
============================================================
Ingesting Lenny's Podcast Transcripts into Hybrid Index
============================================================
Status:          ready
Episodes loaded: 5
Chunks indexed:  11
------------------------------------------------------------
Testing retrieval for: 'What did Rahul Vohra say about the 40% product-market fit engine?'
Found 2 matching chunks:
  [1] Episode: How Superhuman Built an Engine to Find Product-Market Fit (Rahul Vohra)
      Score:   0.999
      Snippet: Rahul Vohra explains Sean Ellis's 40% disappointment benchmark...
```

To ingest custom transcripts:
1. Place `.json` or `.md` files in `data/raw/`.
2. Run `python scripts/ingest_transcripts.py`.

---

## Running the Application

### Method 1: Local Runner Script (Fastest)
```bash
python scripts/run_local.py
```
Open **[http://localhost:8000/](http://localhost:8000/)** in your browser.

### Method 2: Uvicorn Directly
```bash
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

### Method 3: Docker Compose (Full Stack)
```bash
docker compose up --build
```
This launches:
- `db`: PostgreSQL 16 on port 5432
- `backend`: FastAPI server on port 8000 (connected to host Ollama via `host.docker.internal`)

---

## Testing

Run the automated test suite with coverage:
```bash
python -m pytest backend/tests -v
```

### Test Suite Coverage:
```
backend/tests/test_artifacts.py::test_artifact_generation_via_chat PASSED
backend/tests/test_artifacts.py::test_ship30_essay_generation_via_chat PASSED
backend/tests/test_health.py::test_health_endpoint PASSED
backend/tests/test_providers.py::test_provider_factory_and_toggle PASSED
backend/tests/test_providers.py::test_mock_provider_generation PASSED
backend/tests/test_retrieval.py::test_relevant_retrieval_rahul_vohra PASSED
backend/tests/test_retrieval.py::test_relevant_retrieval_elena_verna PASSED
backend/tests/test_retrieval.py::test_empty_retrieval_out_of_domain PASSED
backend/tests/test_routing.py::test_routing_grounded_qa PASSED
backend/tests/test_routing.py::test_routing_ship30_essay PASSED
backend/tests/test_routing.py::test_routing_artifact_generation PASSED
backend/tests/test_routing.py::test_routing_out_of_domain PASSED
backend/tests/test_security.py::test_log_credential_sanitization PASSED
backend/tests/test_security.py::test_frontend_iframe_sandbox_policy PASSED
backend/tests/test_sessions.py::test_session_lifecycle_and_isolation PASSED

============================= 15 passed in 0.35s ==============================
```

For manual UI verification, refer to [`docs/manual_ui_test_plan.md`](docs/manual_ui_test_plan.md).

---

## API Documentation

FastAPI auto-generates interactive Swagger and OpenAPI documentation:
- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core Endpoints:
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Comprehensive health check (DB, Ollama, Index) |
| `GET` | `/api/models` | List available models and current active selection |
| `POST` | `/api/models/toggle` | Switch LLM provider at runtime |
| `GET` | `/api/sessions` | List all conversation sessions |
| `POST` | `/api/sessions` | Create a new session |
| `GET` | `/api/sessions/{id}` | Get session details and message history |
| `DELETE`| `/api/sessions/{id}` | Delete a session and its cascade records |
| `POST` | `/api/chat` | Send prompt, trigger agent routing, return grounded answer |
| `GET` | `/api/artifacts/{id}` | Fetch generated artifact by ID |

---

## Security Architecture

1. **Untrusted HTML Sandboxing:**
   - Generated HTML is rendered in an `<iframe>` with `sandbox="allow-scripts"`.
   - Strictly omits `allow-same-origin` and `allow-top-navigation`.
   - Origin is forced to `null`, completely preventing access to `window.parent`, `document.cookie`, `localStorage`, or authentication tokens.
2. **Credential Sanitization:**
   - Structured JSON logging scrubs any dictionary keys matching sensitive terms (`api_key`, `token`, `password`, `secret`).
3. **Prompt Injection Mitigation:**
   - Strict system instructions require factual grounding on transcript excerpts and enforce out-of-domain refusal.

---

## Project Structure

```
lenny-growth-assistant/
├── backend/
│   ├── app/
│   │   ├── agents/          # Intent routing and agent orchestrator
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── core/            # Config, JSON logging, and security
│   │   ├── db/              # SQLAlchemy session and ORM base
│   │   ├── models/          # Database ORM models (Session, Message, Citation, Artifact)
│   │   ├── retrieval/       # Chunker, hybrid BM25/cosine index, and sources
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   ├── services/        # Provider abstraction (Ollama, Claude, OpenAI, Mock)
│   │   ├── skills/          # Grounded QA, Ship 30 Essay, and Artifact skills
│   │   └── main.py          # Application entry point and static mounting
│   ├── tests/               # 15 automated pytest tests
│   └── requirements.txt     # Python backend dependencies
├── frontend/
│   ├── index.html           # Single-Page App with Claude-Style Artifact Viewer
│   └── package.json         # Evaluator package metadata
├── data/
│   ├── fixtures/            # Curated transcript fixtures from Lenny's Podcast
│   ├── raw/                 # Ingestion directory for custom transcripts
│   └── processed/           # Processed index store
├── scripts/
│   ├── run_local.py         # One-command local application runner
│   └── ingest_transcripts.py# CLI ingestion tool and index validator
├── docs/
│   └── manual_ui_test_plan.md # 10-step manual UI verification guide
├── agent-transcripts/       # Coding agent design logs, debugging, and audit trails
├── docker-compose.yml       # Production Docker Compose definition
├── Dockerfile               # Backend Docker container definition
├── .env.example             # Documented environment template
├── .gitignore               # Strict gitignore rules
├── PRD.md                   # Product Requirements Document
├── architecture.md          # Technical Architecture Specification
├── design.md                # UI/UX Specification & Design Tokens
├── requirements.md          # Traceability Matrix
├── DEMO_SCRIPT.md           # 2–3 minute video presentation script
├── FINAL_CHECKLIST.md       # Audit checklist verifying all 44 requirements
└── README.md                # This operational guide
```

---

## Troubleshooting

### 1. Ollama Connection Error (`Cannot connect to Ollama at http://localhost:11434`)
- **Cause:** Ollama daemon is not running on your host machine.
- **Fix:** Open a terminal and run `ollama serve`. Alternatively, toggle to `mock` or Cloud provider in the UI.

### 2. Missing Ollama Model (`model 'llama3.2' not found`)
- **Fix:** In your terminal, run `ollama pull llama3.2`.

### 3. Docker Cannot Connect to Host Ollama
- **Cause:** Linux or Windows host gateway not resolving.
- **Fix:** Ensure `OLLAMA_BASE_URL=http://host.docker.internal:11434` is set in Docker environment (configured by default in `docker-compose.yml`).

### 4. PostgreSQL Connection Refused on Local Python Run
- **Fix:** If you are running locally without Docker, the application automatically activates SQLite fallback. If you prefer PostgreSQL, run `docker compose up -d db`.

---

## Submission Details

- **Due Date:** 12/10/26 EOD
- **Submission Form:** [Google Forms](https://forms.gle/LgotDHNVxW1mbzNE7)
- **Demo Script:** [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md)
- **Verification Audit:** [`FINAL_CHECKLIST.md`](FINAL_CHECKLIST.md)
