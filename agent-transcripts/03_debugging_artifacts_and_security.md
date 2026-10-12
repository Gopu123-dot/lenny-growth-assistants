# Agent Transcript 03: Artifact Viewer, Security & Debugging

**Agent:** Senior Forward Deployed AI Engineer  
**Date:** October 2026  
**Context:** Artifact Rendering, Security Sandbox & Automated Test Debugging  

---

## 1. Claude-Style Artifact Viewer & Security Architecture

### Problem: Untrusted HTML Artifact Rendering
- User or assistant-generated HTML code cannot simply be injected into the main DOM via `innerHTML` or `dangerouslySetInnerHTML`. Doing so exposes the application to Cross-Site Scripting (XSS), credential theft, cookie hijacking, and parent window redirection.
- **Architectural Solution:**
  - Implemented an isolated `<iframe>` container inside the Artifact Viewer panel.
  - Configured strict sandbox attributes: `sandbox="allow-scripts"`.
  - **Explicitly omitted:**
    - `allow-same-origin`: Ensures the iframe runs under `origin: null`, making it physically impossible for JavaScript inside the iframe to access `window.parent`, `document.cookie`, `localStorage`, or session tokens.
    - `allow-top-navigation`: Blocks malicious code from hijacking the parent browser tab.
    - `allow-popups`: Prevents spam modals or rogue window creation.
  - **Permitted:**
    - Safe local UI interactivity (e.g. checkbox state calculations in the PMF scorecard, interactive slider controls) while remaining completely isolated from the host application.

---

## 2. Bug Encountered & Root Cause Fix during Automated Testing

### Test Failure in `test_artifacts.py` and `test_routing.py`
During the test run of the automated suite, two tests failed:
```
FAILED backend/tests/test_artifacts.py::test_artifact_generation_via_chat
FAILED backend/tests/test_routing.py::test_routing_artifact_generation
AssertionError: assert 'grounded_qa' == 'artifact_generation'
```

### Root Cause Analysis:
- In `backend/app/agents/router.py`, the intent classifier relied on a rigid list of static phrases:
  ```python
  artifact_triggers = ["generate html", "create html", "interactive scorecard", ...]
  ```
- The test query was: `"Generate an interactive HTML scorecard for evaluating onboarding friction."`
- Because the word *"interactive"* appeared between *"generate"* and *"html"*, the static substring check failed, and the query inadvertently fell through to `"grounded_qa"`.

### Systematic Fix:
- Replaced the rigid static substring list with a dual-predicate intent matcher:
  ```python
  has_creation_intent = any(verb in msg for verb in ["generate", "create", "build", "make", "draft", "design", "render", "show me"])
  has_artifact_target = any(target in msg for target in ["html", "css", "scorecard", "calculator", "widget", "dashboard", "artifact"])

  if (has_creation_intent and has_artifact_target) or ...:
      return "artifact_generation"
  ```
- Re-ran the full test suite (`pytest backend/tests -v`).
- **Result:** All 15 tests passed cleanly in 0.35s.

---

## 3. Observability & Credential Scrubbing Verification
- Added automated security test `test_log_credential_sanitization` verifying that sensitive dictionary keys (`api_key`, `authorization`, `password`, `secret`) are recursively replaced with `[REDACTED]` before log emission.
- Verified that all SQL queries, retrieval latencies, and token counts are recorded in structured JSON format.
