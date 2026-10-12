# 2–3 Minute Video Demo Presentation Script

## Product: The Lenny Growth Assistant
**Presenter:** Forward Deployed Engineer  
**Format:** Camera-enabled screen recording (2 to 3 minutes)  
**Target Audience:** Engineering & Product Leadership  

---

### [0:00 – 0:25] 1. Problem & Customer Discovery Framing
**[Camera On + Showing Application Landing Page]**
> "Hi everyone, I'm presenting **The Lenny Growth Assistant**—a production-grade, local-first conversational AI web application built for product managers, growth leads, and founders.
> 
> The core problem we solved: Lenny's Podcast contains over 200+ hours of world-class operator wisdom from leaders like Rahul Vohra, Elena Verna, and Brian Balfour. But when product teams face urgent decisions on PMF or onboarding, scrubbing through hours of audio is impossible, and generic LLMs hallucinate plausible-sounding but completely fabricated advice.
> 
> We built an enterprise copilot that grounds every answer in verified transcripts, traces citations, generates Ship 30 essays, renders live interactive artifacts, and runs completely locally using **Ollama**."

---

### [0:25 – 0:55] 2. Grounded Q&A, Provenance & Contextual Follow-Up
**[Screen Action: Click 'Product-Market Fit Engine' starter card or type query]**
> "Let's ask a fundamental strategic question: *'How did Rahul Vohra build an engine to find Product-Market Fit with the 40% benchmark?'*
> 
> Notice what happens:
> 1. Our hybrid retrieval engine identifies the exact transcript chunks from Superhuman's episode.
> 2. The assistant synthesizes a structured breakdown: Sean Ellis's 40% leading indicator, segmenting High-Expectation Customers, and the 50/50 roadmap rule.
> 3. Look right below the answer: here are the **Grounded Transcript Sources**. We can inspect the exact episode title, guest name, 99.9% match confidence, and the verbatim excerpt from Rahul Vohra.
> 
> Now let's test **multi-turn context**: *'What metrics should I track to know if PMF is improving?'*
> The assistant understands we are still discussing Superhuman's PMF engine, preserving session context without cross-session data leakage."

---

### [0:55 – 1:35] 3. Ship 30 for 30 Essay Skill
**[Screen Action: Click follow-up chip or type 'Write a Ship 30 for 30 essay on why retention breaks before acquisition']**
> "Product operators don't just want chat answers; they need shareable thought-leadership memos. We built a dedicated **Ship 30 for 30 Content Skill** encoding Nicolas Cole and Dickie Bush's writing principles.
> 
> Notice the output:
> - An irresistible hook and headline.
> - Rhythmic cadence with single-sentence hooks and punchy declarations.
> - High scannability with bolded principles, markdown tables, and numbered frameworks.
> - Concrete data points grounded in Elena Verna's leaky bucket principle and Patrick Campbell's 4x pricing advantage.
> - And an actionable 3-part Executive Takeaway at the end."

---

### [1:35 – 2:15] 4. Claude-Style Artifact Viewer & Security Sandboxing
**[Screen Action: Click 'View Generated Artifact' or ask for 'Generate an interactive HTML scorecard for evaluating onboarding funnel']**
> "When visual components or code are created, they shouldn't be trapped in a chat bubble. The assistant opens our Claude-style **Artifact Viewer** side-by-side with the chat.
> 
> Look at the viewer:
> - In the **Preview Tab**, we have a live, interactive PMF and Retention Health Scorecard. I can click the checkboxes, and the score recalculates dynamically.
> - In the **Code Tab**, we see the syntax-highlighted source code with one-click clipboard copying.
> 
> **Security Architecture:** Generated HTML is untrusted content. We isolate it inside an `<iframe>` configured with `sandbox='allow-scripts'`, strictly omitting `allow-same-origin` and `allow-top-navigation`. The iframe runs with `origin: null`, making it physically impossible for the artifact to access application cookies, parent DOM, or auth tokens."

---

### [2:15 – 2:45] 5. Local Ollama Integration & Model Toggle
**[Screen Action: Click the model badge in the top right header]**
> "Let's look at infrastructure. Up here in the header is our active model badge.
> 
> The application is currently running on **Ollama** using `llama3.2` locally on my laptop. Zero cloud API calls, zero latency cost, complete data privacy.
> 
> If we want frontier reasoning, I click the badge, select **Anthropic Claude 3.5 Sonnet** or **OpenAI**, and the runtime switches instantly without restarting the application or changing code."

---

### [2:45 – 3:00] 6. Key Technical Trade-Off & Wrap-Up
**[Camera On + Closing Remarks]**
> "To close, let's discuss **one key technical trade-off**:
> We chose a **hybrid retrieval model (BM25 + TF-IDF cosine vectors with guest boosting)** over a purely remote vector database like Pinecone.
> 
> *The Trade-off:* While dense neural embeddings capture subtle metaphors, they require heavy dependencies, remote API calls, and struggle with exact proper nouns like guest names. Our local hybrid engine delivers sub-5ms retrieval directly in Python, runs offline with zero setup friction, and enables 100% test reproducibility.
> 
> The entire project runs with a single command via Docker Compose or local Python runner.
> Thank you for your time!"
