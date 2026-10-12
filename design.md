# Frontend Design System & UI/UX Specification

## Product: The Lenny Growth Assistant
**Document:** UI/UX Specification & Design Documentation  
**Version:** 1.0.0  
**Author:** Forward Deployed Engineering Team  
**Status:** Approved for Implementation  

---

## 1. UI/UX Principles & Philosophy

*The Lenny Growth Assistant* is designed as an internal enterprise copilot for growth and product operators. It departs from toy chatbot interfaces by adhering to five core product design principles:

1. **Information Density with High Scannability:** Product operators need to parse key takeaways rapidly. The interface emphasizes clear typographic hierarchy, generous line heights, formatted tables, bullet points, and selective bolding.
2. **Transparent Provenance & Trust:** Every assertion is visually linked to a primary source. Source citations are presented as structured, expandable cards with episode numbers, guest names, and timestamps, not generic footnote links.
3. **Workspace Fluidity (Claude-Style Artifacts):** Content synthesis shouldn't remain trapped in a narrow vertical chat thread. When an essay, checklist, or HTML framework is created, it seamlessly opens in a dedicated side-by-side **Artifact Viewer** workspace.
4. **Transparent System State:** Users and evaluators must always know the active model (e.g., `Ollama: llama3.2` vs. `Anthropic: claude-3-5-sonnet`), retrieval latency, and system health through persistent, subtle status badges.
5. **Zero-Latency Resilience:** Instant UI feedback during async actions, graceful degradation toasts when services fail, and robust keyboard shortcuts for high-velocity power users.

---

## 2. Information Architecture & Spatial Layout

The viewport is partitioned into a 3-zone layout that adapts dynamically based on whether an artifact is active.

```
+---------------------------------------------------------------------------------------------------------+
|                                  TOP APPLICATION BAR                                                   |
| [Logo] The Lenny Growth Assistant          [Active Model Badge: Ollama / Llama 3.2]    [Health: OK (12ms)] |
+-----------------------+---------------------------------------------------+-----------------------------+
|    LEFT SIDEBAR       |                   MAIN CHAT AREA                  |       ARTIFACT VIEWER       |
|                       |                                                   |     (Side-by-Side Panel)    |
| [+ New Chat]          | [Active Session Title]                            | [Artifact Title]  [Type]   |
| [Search Sessions]     |                                                   | [Preview] [Code] [Copy] [X] |
|                       | +-----------------------------------------------+ | +-------------------------+ |
| SESSION LIST:         | | User: What did Rahul Vohra say about PMF?     | | |                         | |
| > Superhuman PMF      | +-----------------------------------------------+ | |  Interactive Sandboxed  | |
|   Onboarding Funnel   |                                                   | |  Rendering of HTML/CSS  | |
|   Pricing Experiments | +-----------------------------------------------+ | |  or Formatted Markdown  | |
|                       | | Assistant: Rahul Vohra's framework focuses on | | |                         | |
| SYSTEM STATUS:        | | the 40% 'very disappointed' metric...         | | |                         | |
| Transcripts: 12       | |                                               | | |                         | |
| Chunks: 184           | | [Source: Rahul Vohra - Superhuman PMF Engine] | | |                         | |
| Provider: Ollama      | +-----------------------------------------------+ | |                         | |
| Port: 11434           |                                                   | |                         | |
|                       | [Prompt Input: Ask a growth question...  [Send]]  | |                         | |
+-----------------------+---------------------------------------------------+-----------------------------+
```

---

## 3. Screen Breakdown & Interaction States

### 3.1 Empty State (Zero-State Onboarding)
When a user launches the app or creates a new session, the chat view presents a welcoming hero section instead of a blank white screen:
- **Hero Title:** "The Lenny Growth Assistant"
- **Subtitle:** "Grounded product strategy and growth advice from over 200+ Lenny's Podcast transcripts."
- **Knowledge Badge:** "12 Curated Episodes Indexed • 180+ Chunks • Real-Time Grounding"
- **Clickable Prompt Starter Cards:**
  1. *Product-Market Fit:* "How does Rahul Vohra measure PMF, and what is the 40% benchmark?"
  2. *Growth Loops & PLG:* "What does Elena Verna recommend for self-serve vs. sales-assist onboarding?"
  3. *Ship 30 Essay:* "Write a Ship 30 for 30 essay on why product retention breaks before acquisition."
  4. *Interactive Framework:* "Generate an interactive HTML scorecard for evaluating onboarding friction."

### 3.2 Active Chat State
- **User Messages:** Right-aligned bubbles with a subtle slate-gray background, distinct avatar, and timestamp.
- **Assistant Messages:** Left-aligned cards with crisp typography, Markdown parsing (bolding, lists, code blocks with syntax highlighting), and citation blocks.
- **Citation Badges:** Rendered beneath the text with an episode icon, guest name, episode title, and an "Inspect Source" disclosure toggle revealing the exact matched transcript excerpt and cosine similarity score.
- **Suggested Follow-up Chips:** Horizontal scrollable pills offering natural logical follow-ups (e.g., "What are the counterarguments?", "How do you calculate this metric?").

### 3.3 Loading & Processing States
- **Thinking Indicator:** Animated pulsing wave with status text: *"Retrieving transcript chunks..."* transitioning to *"Synthesizing response with Ollama..."*.
- **Streaming Response:** Progressive token streaming to provide immediate visual feedback.
- **Disabled Send State:** The input box and send button are disabled during active generation with an optional "Stop Generating" action.

### 3.4 Error States
- **Graceful Error Banners:** Clear, actionable alerts (e.g., *"Ollama daemon is not reachable at localhost:11434. Please run 'ollama serve' or switch to Cloud Provider in settings."*).
- **Out-of-Domain Refusal:** When a prompt cannot be grounded in transcripts, the assistant displays a polite yellow notice: *"I searched the indexed podcast transcripts but could not find discussions supporting this topic. I only provide answers grounded in Lenny's knowledge base."*
- **Retry Action:** Every error card provides a one-click "Retry" button.

### 3.5 Artifact Viewer State
- **Split-Screen Workspace:** Slides in smoothly from the right side of the screen taking 45% of viewport width on desktop.
- **Header Controls:**
  - Artifact Title and Type indicator (`Markdown Document`, `Interactive HTML Widget`, `CSS Layout`).
  - Action Bar:
    - **Preview Button:** Switches to live visual view.
    - **Code Button:** Switches to raw syntax-highlighted code editor view.
    - **Copy Button:** Copies content to clipboard with temporary "Copied!" checkmark feedback.
    - **Close Button (`✕`):** Dismisses viewer and expands chat back to full width.
- **Sandboxed Container:** Secure `<iframe>` with isolated styles and zero access to parent DOM.

---

## 4. Design System & Style Tokens

### 4.1 Color Palette
- **Background Base:** `#0F172A` (Slate 900 - Dark mode default for developer polish) / `#FFFFFF` (Light mode clean neutral)
- **Surface Card:** `#1E293B` (Slate 800) with subtle `#334155` border
- **Primary Brand Accent:** `#6366F1` (Indigo 500) / `#4F46E5` (Indigo 600)
- **Growth Green (Grounded):** `#10B981` (Emerald 500) for source citations and success states
- **Warning Amber:** `#F59E0B` (Amber 500) for out-of-domain notices
- **Error Rose:** `#F43F5E` (Rose 500) for network and model timeouts
- **Typography:**
  - Font Family: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, sans-serif
  - Monospace: `JetBrains Mono`, `Fira Code`, `Consolas`, monospace for code blocks

### 4.2 Spacing & Layout
- Standard 8px grid system (`4px`, `8px`, `12px`, `16px`, `24px`, `32px`).
- Border radius: `8px` (`rounded-lg`) for buttons and cards; `12px` (`rounded-xl`) for main containers.

---

## 5. Responsive Behavior

| Breakpoint | Sidebar | Chat Area | Artifact Viewer |
| :--- | :--- | :--- | :--- |
| **Desktop (≥ 1280px)** | Expanded (280px width) | Center stage (55% width) | Side-by-side (45% width) when active |
| **Tablet (768px – 1279px)** | Collapsible drawer (overlay) | Full width | Side-by-side or tabbed overlay |
| **Mobile (< 768px)** | Off-canvas drawer via hamburger | Full width (100%) | Full-screen bottom sheet with swipe-down to dismiss |

---

## 6. Accessibility Considerations (WCAG 2.1 AA)

1. **Color Contrast:** All text elements exceed the 4.5:1 contrast ratio against their respective background surfaces.
2. **Keyboard Navigation:**
   - `Tab` / `Shift+Tab`: Logical traversal through sidebar sessions, chat messages, input field, and artifact tabs.
   - `Enter`: Submits message (with `Shift+Enter` for multiline breaks).
   - `Esc`: Closes artifact viewer or modal drawers.
   - `Ctrl/Cmd + K`: Focuses search or triggers New Chat.
3. **Screen Readers:** ARIA live regions (`aria-live="polite"`) on the chat stream ensure screen readers announce incoming assistant responses.
4. **Accessible Forms:** All inputs include explicit `<label>` or `aria-label` tags and visible focus rings (`focus:ring-2 focus:ring-indigo-500`).
