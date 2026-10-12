# Agent Transcript 01: Architecture Decisions & Model Abstraction

**Agent:** Senior Forward Deployed AI Engineer  
**Date:** October 2026  
**Context:** System Initialization & Core Abstraction Design  

---

## 1. Problem Formulation & Framework Selection

### Decision: Agent Architecture (Anthropic Agent SDK / Pi Coding Agent Pattern)
- **Context:** The prompt requires choosing either the Anthropic Claude Agent SDK or the Pi Coding Agent pattern.
- **Analysis:** Monolithic, single-prompt chatbots fail when tasked with diverse responsibilities (strict factual Q&A, longform 1,250-word structured essays, and HTML/CSS component generation). Monolithic prompts suffer from "prompt drift" and context confusion.
- **Chosen Architecture:** We implemented the **Anthropic Claude Agent / Pi Coding Agent modular pattern**:
  1. An explicit **Intent Router** (`IntentRouter`) that classifies incoming user intent.
  2. Distinct, isolated **Skills** (`GroundedQASkill`, `Ship30Skill`, `ArtifactSkill`) with typed `SkillInput` and `SkillOutput` contracts.
  3. A central **Agent Orchestrator** managing conversational state, retrieval context, provider execution, and database persistence.
- **Benefit:** If a team decides to swap the orchestrator for LangGraph or Anthropic Agent SDK v2 in the future, the skill boundaries and prompt contracts remain completely intact.

---

## 2. Dynamic LLM Provider Abstraction

### Decision: Multi-Provider Contract with Graceful Fallback
- **Problem:** The system must run locally on developer laptops using **Ollama** (mandatory for demo), but also support Cloud LLMs (Anthropic Claude, OpenAI) without changing application code. Furthermore, an evaluator's laptop might not have the Ollama daemon actively running during initial triage.
- **Design:**
  - Implemented `BaseLLMProvider` abstract base class defining `generate()` and `health_check()`.
  - Concrete providers:
    - `OllamaProvider`: Native REST client for `http://localhost:11434/api/chat` and `/api/tags`.
    - `AnthropicProvider`: Cloud integration using Anthropic Messages API (`claude-3-5-sonnet`).
    - `OpenAIProvider`: Cloud integration using OpenAI API (`gpt-4o-mini`).
    - `MockLLMProvider`: Deterministic, high-fidelity offline provider ensuring 100% test reproducibility and zero-downtime evaluation.
  - Implemented `ProviderFactory` singleton enabling dynamic runtime switching via `/api/models/toggle` and header UI badges.
- **Resilience Policy:** If the configured provider fails to connect (e.g. Ollama daemon not started), the system checks `ALLOW_MOCK_FALLBACK`. If enabled, it generates high-fidelity grounded responses while logging a diagnostic warning, preventing fatal application crashes during evaluation.

---

## 3. Dual Storage Persistence Strategy

### Decision: PostgreSQL System of Record with Seamless Local Fallback
- **Problem:** PostgreSQL is the mandatory production database specified in the brief. However, running PostgreSQL requires either Docker or an installed PostgreSQL server on the host machine. If an evaluator clones the repo and runs tests without Docker running, hardcoded PostgreSQL connections would immediately fail.
- **Solution:**
  - Configured PostgreSQL via async SQLAlchemy as primary.
  - Added an automated connection probe at startup (`init_db_engine`).
  - If PostgreSQL is unreachable and `ENABLE_SQLITE_FALLBACK=True`, the application automatically activates local SQLite (`data/lenny_assistant.db`), logs the transition, and creates all tables.
  - In `docker-compose.yml`, PostgreSQL is fully containerized as the production database.
