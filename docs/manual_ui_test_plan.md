# Manual UI Verification Test Plan

## Product: The Lenny Growth Assistant
**Target:** Evaluator & QA Verification  
**Coverage:** 10 Core User Journeys  

---

### Test Case 1: Landing Experience & Zero-State Onboarding
- **Action:** Open `http://localhost:8000/` in a browser.
- **Expected Result:**
  - Header displays "The Lenny Growth Assistant" with "Grounded RAG" badge.
  - Active provider badge shows "Ollama (llama3.2)" with green indicator.
  - Sidebar shows knowledge base stats (11 chunks, 5 episodes, PostgreSQL/SQLite).
  - Main area displays zero-state hero with 4 clickable prompt starter cards.

### Test Case 2: Grounded Q&A with Verbatim Citation
- **Action:** Click the "Product-Market Fit Engine" starter card or send *"How did Rahul Vohra build an engine to find Product-Market Fit with the 40% benchmark?"*
- **Expected Result:**
  - Input field is disabled with animated thinking indicator.
  - Assistant responds with structured Markdown explaining Sean Ellis's 40% benchmark, High-Expectation Customers, and the 50/50 roadmap allocation.
  - Beneath the message, an expandable "Grounded Transcript Sources" block appears citing Rahul Vohra, episode title, match score (≥90%), and verbatim quote snippet.
  - Suggested follow-up chips appear at the bottom.

### Test Case 3: Contextual Multi-Turn Follow-Up
- **Action:** In the same session, send *"What metrics should I track to know if PMF is improving?"*
- **Expected Result:**
  - The assistant understands the context is Superhuman/PMF from the prior turn.
  - It references the movement of the 40% score (e.g., Superhuman moving from 22% to 58%) and the segment-level metrics.
  - New citations appear.

### Test Case 4: Strict Session Isolation
- **Action:**
  1. Click "+ New Conversation" in the left sidebar.
  2. Ask *"What did Patrick Campbell say about SaaS pricing?"*
  3. Switch back to the first conversation by clicking it in the sidebar.
- **Expected Result:**
  - First conversation displays Rahul Vohra's PMF history.
  - Second conversation displays Patrick Campbell's pricing history.
  - No messages or citations bleed between the two sessions.

### Test Case 5: Ship 30 for 30 Content Skill
- **Action:** Send *"Write a Ship 30 for 30 essay on why retention breaks before acquisition."*
- **Expected Result:**
  - Intent router selects `ship30_essay`.
  - Assistant generates an ~1,250-word structured atomic essay featuring:
    - Irresistible Hook / Headline.
    - Cadenced narrative progression.
    - Elena Verna's leaky bucket principle and Time-to-Aha.
    - Brian Balfour's growth loops.
    - Patrick Campbell's 4x pricing lever.
    - Skimmable bold emphasis and bullet points.
    - Executive Takeaway checklist.
  - An artifact button appears: *"View Generated Artifact: Ship 30 for 30 Essay"*.

### Test Case 6: Claude-Style Artifact Viewer
- **Action:** Click the artifact button or send *"Generate an interactive HTML scorecard for evaluating our onboarding funnel."*
- **Expected Result:**
  - The Artifact Viewer slides in side-by-side with the chat.
  - **Preview Tab:** Renders the interactive PMF/Retention scorecard inside an isolated `<iframe>`. Clicking the checkboxes dynamically updates the calculated percentage in real time.
  - **Code Tab:** Shows syntax-highlighted HTML/CSS/JS source code.
  - **Copy Action:** Copies raw code to clipboard with "Copied!" toast confirmation.
  - **Close Action:** Clicking `✕` closes the viewer and expands the chat back to full width.

### Test Case 7: Artifact Security Sandboxing
- **Action:** Inspect the `<iframe>` element in Developer Tools (F12).
- **Expected Result:**
  - `<iframe sandbox="allow-scripts">` is present.
  - `allow-same-origin` is absent.
  - `allow-top-navigation` is absent.
  - The iframe runs under `origin: null`, preventing access to cookies or parent window.

### Test Case 8: Dynamic Model Switching
- **Action:** Click the active provider badge in the header ("Ollama (llama3.2)").
- **Expected Result:**
  - Modal opens listing Local Ollama, Anthropic Claude, and OpenAI.
  - Clicking a different provider immediately updates the badge and sends future messages to the selected provider.

### Test Case 9: Out-of-Domain Refusal
- **Action:** Send *"Explain the French Revolution and the storming of the Bastille."*
- **Expected Result:**
  - The assistant refuses politely without hallucinating, stating that the knowledge base is grounded specifically in Lenny's podcast transcripts on product management and growth.

### Test Case 10: Session Deletion & Persistence
- **Action:** Hover over a conversation in the sidebar and click the trash can icon. Refresh the browser page (`F5`).
- **Expected Result:**
  - Deleted session is removed from PostgreSQL.
  - Remaining sessions persist across page refresh.
