"""Deterministic test and fallback provider for offline development and CI."""

import time
import re
from typing import List, Dict, Any, Optional
from app.services.base_provider import BaseLLMProvider, ChatMessage, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    """Provides high-quality grounded responses for local test verification and fallback."""

    def __init__(self, model_name: str = "deterministic-evaluator"):
        super().__init__(model_name)

    async def generate(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        start_time = time.perf_counter()

        last_user_message = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user_message = m.content
                break

        prompt_lower = last_user_message.lower()
        content = ""

        # Check if the prompt is an explicit out-of-domain query
        if any(unrelated in prompt_lower for unrelated in ["quantum physics", "recipe for pizza", "french revolution", "astrophysics"]):
            content = (
                "I searched the available transcript knowledge base for Lenny's Podcast, "
                "but I could not find information supporting this topic. "
                "I am specifically grounded in Lenny's interviews on product management, growth, onboarding, retention, and pricing."
            )

        # Check if Ship 30 essay is requested
        elif "ship 30" in prompt_lower or "essay" in prompt_lower or "article" in prompt_lower:
            content = self._generate_ship30_essay(last_user_message, system_prompt or "")

        # Check if HTML/CSS artifact is requested
        elif "html" in prompt_lower or "artifact" in prompt_lower or "component" in prompt_lower or "widget" in prompt_lower or "scorecard" in prompt_lower:
            content = self._generate_html_artifact(last_user_message)

        # Grounded Q&A response
        else:
            content = self._generate_grounded_answer(last_user_message, system_prompt or "")

        latency_ms = (time.perf_counter() - start_time) * 1000

        return LLMResponse(
            content=content,
            provider="mock",
            model=self.model_name,
            latency_ms=round(latency_ms, 2),
            token_usage={"prompt_tokens": len(last_user_message.split()), "completion_tokens": len(content.split())},
            is_fallback=True,
            raw_response={"status": "mock_generated"},
        )

    def _generate_grounded_answer(self, query: str, context: str) -> str:
        q = query.lower()
        if "rahul" in q or "vohra" in q or "pmf" in q or "superhuman" in q:
            return (
                "Based strictly on Lenny's interview with **Rahul Vohra** (*Founder & CEO of Superhuman*):\n\n"
                "Rahul emphasizes that **Product-Market Fit (PMF)** is not a binary, emotional gut feeling—it is a measurable engineering discipline.\n\n"
                "### The 40% Benchmark\n"
                "- Rahul uses Sean Ellis's leading indicator question: *'How would you feel if you could no longer use the product?'*\n"
                "- Startups where **40% or more** answer **'Very disappointed'** tend to find sustainable hyper-growth. Below 40%, companies almost invariably struggle.\n"
                "- Superhuman initially scored **22%**, which felt like a gut punch, but they built an engine to systematically move that score.\n\n"
                "### The 4-Step Engine\n"
                "1. **Segment to Find the High-Expectation Customer (HXC):** Filter your data to users who truly need the product. Filtering for users whose jobs depended on email immediately boosted Superhuman's score from 22% to 32%.\n"
                "2. **Analyze Feedback by Cohort:** Focus on what the 'Very disappointed' users love (speed, shortcuts, triage), and what is holding back the 'Somewhat disappointed' cohort. Crucially: *throw away feedback from 'Not disappointed' users* as they will steer the roadmap astray.\n"
                "3. **50/50 Resource Allocation:** Allocate 50% of roadmap capacity to doubling down on core strengths (speed, offline mode) and 50% to resolving high-leverage objections of on-the-fence users (mobile apps, integrations).\n"
                "4. **Continuous Measurement:** Tracking this over 3 quarters raised Superhuman's PMF score to **58%**, creating full launch conviction.\n\n"
                "*(Source: Lenny's Podcast Episode with Rahul Vohra - How Superhuman Built an Engine to Find Product-Market Fit)*"
            )
        elif "elena" in q or "verna" in q or "onboarding" in q or "retention" in q or "plg" in q:
            return (
                "Based strictly on Lenny's interview with **Elena Verna** (*Head of Growth at Amplitude/Miro/Dropbox*):\n\n"
                "### 1. Retention is the Foundation of All Growth\n"
                "- Acquisition is a vanity metric that burns marketing budget if the product has a 'leaky bucket'.\n"
                "- Retention compounds exponentially: a 5% increase in retention dramatically increases 3-year enterprise value.\n\n"
                "### 2. Time-to-Aha! Onboarding\n"
                "- The biggest onboarding mistake is creating feature tours or UI walkthroughs. Users arrive with an emotional problem to solve.\n"
                "- Onboarding must ruthlessly minimize **Time to Aha! Moment**. For example, at Miro, the Aha moment was placing a first sticky note and inviting a teammate to see it live. Anything not accelerating this moment should be eliminated.\n\n"
                "### 3. Freemium vs. Free Trial\n"
                "- **Free Trial:** Time-bound purchasing evaluation (best when value is proven within 7 days and marginal costs are high).\n"
                "- **Freemium:** Habitual engagement channel (essential for collaborative products like Slack or Figma requiring weeks of network effect formation).\n\n"
                "*(Source: Lenny's Podcast Episode with Elena Verna - The Ultimate Guide to PLG and Retention)*"
            )
        elif "brian" in q or "balfour" in q or "loop" in q or "four fits" in q:
            return (
                "Based strictly on Lenny's interview with **Brian Balfour** (*Founder & CEO of Reforge*):\n\n"
                "### 1. The Death of the Linear Funnel\n"
                "- Traditional linear funnels (AARRR) create transactional silos where you must constantly pour more spend into the top.\n"
                "- World-class companies scale through **Growth Loops**—closed systems where the output of one cycle (a design, an invite, revenue) directly becomes the input for the next cycle.\n\n"
                "### 2. Primary Loop Archetypes\n"
                "- **Viral / Collaborative Loops (Figma, Docs):** Using the product naturally generates invites to collaborators.\n"
                "- **Content / SEO Loops (Pinterest, Yelp):** User activity produces indexable content, driving organic search traffic.\n"
                "- **Paid / Capital Loops:** High gross margins fund reinvestment in customer acquisition.\n\n"
                "### 3. The Four Fits Framework\n"
                "- PMF alone is insufficient. You must align **Market-Product Fit, Product-Channel Fit, Channel-Model Fit, and Model-Market Fit**.\n"
                "- Products must be built to fit channels; channels will never morph to fit your product.\n\n"
                "*(Source: Lenny's Podcast Episode with Brian Balfour - Growth Loops and the Four Fits)*"
            )
        elif "shreyas" in q or "doshi" in q or "lno" in q or "metric" in q:
            return (
                "Based strictly on Lenny's interview with **Shreyas Doshi** (*former Stripe, Twitter, Google*):\n\n"
                "### 1. The LNO Framework\n"
                "- Applying 10/10 effort to everything guarantees burnout and strategic mediocrity.\n"
                "- **L (Leverage):** 10x multiplier tasks (Strategy, PRDs, Pricing, Key Hires). Require 10/10 perfectionist dedication.\n"
                "- **N (Neutral):** Maintenance tasks (Sprint planning, regular updates). 7/10 good quality is optimal.\n"
                "- **O (Overhead):** Admin chores (Expense reports, routine email). Batch at 4/10 or 5/10 quality.\n\n"
                "### 2. Goodhart's Law & Counter-Metrics\n"
                "- When a measure becomes a target, teams gamify it (e.g. clickbait notifications for DAU).\n"
                "- Every North Star metric **must be paired with a Counter-Metric** (e.g., DAU paired with 90-day churn or unsubscribe rates).\n\n"
                "*(Source: Lenny's Podcast Episode with Shreyas Doshi - The LNO Framework and High-Agency PM)*"
            )
        elif "pricing" in q or "patrick" in q or "campbell" in q:
            return (
                "Based strictly on Lenny's interview with **Patrick Campbell** (*Founder & CEO of ProfitWell*):\n\n"
                "### 1. The 4x Monetization Advantage\n"
                "- A 1% improvement in acquisition yields ~3.2% bottom-line growth, whereas a **1% improvement in pricing/packaging yields 11.1%**.\n"
                "- Monetization has 4x the leverage of acquisition because it directly expands margin without incremental CAC.\n\n"
                "### 2. Value Metrics Over Per-Seat Pricing\n"
                "- Charging per seat penalizes collaboration and strangles product-led expansion.\n"
                "- Align pricing with a true **Value Metric** (e.g. HubSpot charges per marketing contact; Zapier per task run). As your customer succeeds, revenue expands organically.\n\n"
                "*(Source: Lenny's Podcast Episode with Patrick Campbell - The Science of SaaS Pricing)*"
            )
        else:
            return (
                "Here is what Lenny's interview knowledge base reveals on this topic:\n\n"
                "Top product and growth leaders emphasize grounding product strategy in rigorous quantitative benchmarks and customer behavior.\n\n"
                "- **Retention First:** Elena Verna proves that retention must be stabilized before scaling acquisition.\n"
                "- **Measurable PMF:** Rahul Vohra demonstrates that Sean Ellis's 40% disappointment benchmark provides a clear roadmap for feature prioritization.\n"
                "- **Compounding Loops:** Brian Balfour illustrates why compounding growth loops outperform linear marketing funnels.\n\n"
                "*(Source: Lenny's Podcast Transcripts Archive)*"
            )

    def _generate_ship30_essay(self, query: str, context: str) -> str:
        return (
            "# The Retention Trap: Why 90% of Startups Scale Acquisition Off a Cliff\n\n"
            "**Most founders believe their growth problem is top-of-funnel.**\n\n"
            "They spend $50,000 on Facebook ads.\n"
            "They celebrate 10,000 signups on Product Hunt.\n"
            "Then, 90 days later, their revenue chart looks like a flatline.\n\n"
            "Here is the brutal truth uncovered across 200+ interviews on *Lenny's Podcast*:\n\n"
            "> **Acquisition is a vanity metric. Retention is the only proof of value.**\n\n"
            "---\n\n"
            "## 1. The Leaky Bucket Delusion\n\n"
            "When growth stalls, the amateur PM's instinct is to buy more traffic.\n\n"
            "Elena Verna (*Head of Growth at Amplitude and Miro*) calls this the **'Expensive Treadmill'**:\n"
            "- If your 30-day cohort retention is 8%, you don't have a growth engine.\n"
            "- You have a furnace burning investor capital.\n"
            "- Pouring more water into a bucket with five holes doesn't fix the bucket—it just wets the floor.\n\n"
            "A **5% improvement in retention** increases long-term enterprise valuation by over 30% through compounding compounding cohorts.\n\n"
            "---\n\n"
            "## 2. The 40% PMF Benchmark You Can't Fake\n\n"
            "How do you know if your retention is fundamentally fixed?\n\n"
            "Rahul Vohra (*CEO of Superhuman*) reverse-engineered this into an exact mathematical test:\n\n"
            "Ask your active users one question:\n"
            "> *\"How would you feel if you could no longer use the product tomorrow?\"*\n\n"
            "1. **Very disappointed**\n"
            "2. **Somewhat disappointed**\n"
            "3. **Not disappointed**\n\n"
            "If **40% or more** say *'Very disappointed'*, you have product-market fit.\n"
            "When Superhuman first measured this in 2017, their score was **22%**.\n\n"
            "Instead of launching anyway, Vohra built an engine:\n"
            "- Filter for High-Expectation Customers (users whose daily work relies on the tool).\n"
            "- Discard all feedback from 'Not disappointed' users (they poison the roadmap).\n"
            "- Allocate 50% of roadmap to doubling down on core delight and 50% to on-the-fence objections.\n\n"
            "Within 9 months, their score reached **58%**.\n\n"
            "---\n\n"
            "## 3. The Onboarding Sin: Feature Tours Kill Momentum\n\n"
            "Once PMF is established, the biggest leak occurs in the first 120 seconds of onboarding.\n\n"
            "Product managers love tooltips, multi-step checklists, and product tours.\n"
            "**Users hate them.**\n\n"
            "As Elena Verna noted at Miro:\n"
            "- Users arrive with an urgent, emotional problem to solve.\n"
            "- Your onboarding exists for one metric: **Time to Aha! Moment**.\n"
            "- At Miro, that moment was dropping one sticky note on a canvas and seeing a teammate move their cursor.\n\n"
            "Cut every form field, every verification modal, and every welcome screen that sits between the user and that moment.\n\n"
            "---\n\n"
            "## 4. Replace Linear Funnels With Closed Loops\n\n"
            "Brian Balfour (*CEO of Reforge*) argues that linear funnels (AARRR) force companies into paid acquisition traps.\n\n"
            "The world's greatest companies scale through **Self-Reinforcing Loops**:\n\n"
            "- **Viral / Collaborative Loops:** Figma and Google Docs turn usage into invitations.\n"
            "- **Content / SEO Loops:** Yelp and Pinterest turn user actions into indexed search pages.\n"
            "- **Capital Loops:** High-margin subscriptions directly fund the next acquisition campaign.\n\n"
            "If your product does not naturally produce the input for the next cohort, you will eventually reach a CAC plateau where growth stalls.\n\n"
            "---\n\n"
            "## 5. The Pricing Multiplier Nobody Talks About\n\n"
            "Finally, Patrick Campbell (*ProfitWell*) evaluated pricing data across 30,000 SaaS companies:\n\n"
            "| Growth Lever | Bottom-Line Impact of 1% Improvement |\n"
            "| :--- | :--- |\n"
            "| **Acquisition** | **+3.2%** |\n"
            "| **Retention** | **+6.7%** |\n"
            "| **Monetization (Pricing)** | **+11.1%** |\n\n"
            "Monetization is **4x more powerful than acquisition** because every pricing dollar drops straight to gross margin.\n\n"
            "Stop charging per-seat if you want viral growth—per-seat pricing penalizes collaboration. Pick a **Value Metric** (contacts, tasks, storage) that expands automatically as your customer wins.\n\n"
            "---\n\n"
            "## The Executive Takeaway\n\n"
            "Before you increase your marketing budget next month, run this 3-step audit:\n\n"
            "1. **Survey your users** on the Sean Ellis 40% disappointment scale.\n"
            "2. **Strip your onboarding** down to the fastest path to the Aha moment.\n"
            "3. **Align your value metric** with customer success, not headcounts.\n\n"
            "Build the foundation first. Compounding growth takes care of the rest."
        )

    def _generate_html_artifact(self, query: str) -> str:
        return (
            "```html\n"
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "  <meta charset=\"UTF-8\">\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            "  <title>Growth Framework Scorecard</title>\n"
            "  <style>\n"
            "    :root {\n"
            "      --primary: #4f46e5;\n"
            "      --bg: #0f172a;\n"
            "      --surface: #1e293b;\n"
            "      --text: #f8fafc;\n"
            "      --text-muted: #94a3b8;\n"
            "      --border: #334155;\n"
            "      --accent: #10b981;\n"
            "    }\n"
            "    body {\n"
            "      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;\n"
            "      background: var(--bg);\n"
            "      color: var(--text);\n"
            "      margin: 0;\n"
            "      padding: 24px;\n"
            "      box-sizing: border-box;\n"
            "    }\n"
            "    .container {\n"
            "      max-width: 680px;\n"
            "      margin: 0 auto;\n"
            "      background: var(--surface);\n"
            "      border: 1px solid var(--border);\n"
            "      border-radius: 12px;\n"
            "      padding: 24px;\n"
            "      box-shadow: 0 10px 25px rgba(0,0,0,0.3);\n"
            "    }\n"
            "    h1 {\n"
            "      font-size: 20px;\n"
            "      margin-top: 0;\n"
            "      color: #ffffff;\n"
            "      display: flex;\n"
            "      align-items: center;\n"
            "      gap: 8px;\n"
            "    }\n"
            "    .badge {\n"
            "      background: rgba(79, 70, 229, 0.2);\n"
            "      color: #818cf8;\n"
            "      font-size: 12px;\n"
            "      padding: 4px 8px;\n"
            "      border-radius: 6px;\n"
            "      border: 1px solid rgba(79, 70, 229, 0.4);\n"
            "    }\n"
            "    .score-box {\n"
            "      background: rgba(16, 185, 129, 0.1);\n"
            "      border: 1px solid rgba(16, 185, 129, 0.3);\n"
            "      border-radius: 8px;\n"
            "      padding: 16px;\n"
            "      margin-bottom: 20px;\n"
            "      display: flex;\n"
            "      justify-content: space-between;\n"
            "      align-items: center;\n"
            "    }\n"
            "    .score-value {\n"
            "      font-size: 28px;\n"
            "      font-weight: 700;\n"
            "      color: var(--accent);\n"
            "    }\n"
            "    .item {\n"
            "      border-bottom: 1px solid var(--border);\n"
            "      padding: 12px 0;\n"
            "      display: flex;\n"
            "      align-items: center;\n"
            "      justify-content: space-between;\n"
            "    }\n"
            "    .item:last-child { border-bottom: none; }\n"
            "    .label {\n"
            "      font-size: 14px;\n"
            "      color: var(--text);\n"
            "    }\n"
            "    .subtext {\n"
            "      font-size: 12px;\n"
            "      color: var(--text-muted);\n"
            "      margin-top: 2px;\n"
            "    }\n"
            "    input[type=\"checkbox\"] {\n"
            "      width: 18px;\n"
            "      height: 18px;\n"
            "      cursor: pointer;\n"
            "      accent-color: var(--primary);\n"
            "    }\n"
            "  </style>\n"
            "</head>\n"
            "<body>\n"
            "  <div class=\"container\">\n"
            "    <h1>PMF & Retention Health Scorecard <span class=\"badge\">Lenny Growth Model</span></h1>\n"
            "    <div class=\"score-box\">\n"
            "      <div>\n"
            "        <div style=\"font-size: 12px; color: var(--text-muted); text-transform: uppercase;\">Calculated Readiness</div>\n"
            "        <div style=\"font-size: 14px; font-weight: 600;\">Product-Market Fit & Scale Index</div>\n"
            "      </div>\n"
            "      <div class=\"score-value\" id=\"score-display\">40%</div>\n"
            "    </div>\n"
            "    <div class=\"item\">\n"
            "      <div>\n"
            "        <div class=\"label\">Rahul Vohra's 40% Disappointment Survey</div>\n"
            "        <div class=\"subtext\">&ge;40% of users state they would be 'very disappointed'</div>\n"
            "      </div>\n"
            "      <input type=\"checkbox\" checked onchange=\"updateScore()\">\n"
            "    </div>\n"
            "    <div class=\"item\">\n"
            "      <div>\n"
            "        <div class=\"label\">Elena Verna's Time-to-Aha Onboarding</div>\n"
            "        <div class=\"subtext\">First core value experienced within 120 seconds</div>\n"
            "      </div>\n"
            "      <input type=\"checkbox\" checked onchange=\"updateScore()\">\n"
            "    </div>\n"
            "    <div class=\"item\">\n"
            "      <div>\n"
            "        <div class=\"label\">Brian Balfour's Compounding Growth Loop</div>\n"
            "        <div class=\"subtext\">User action directly feeds next user acquisition cycle</div>\n"
            "      </div>\n"
            "      <input type=\"checkbox\" onchange=\"updateScore()\">\n"
            "    </div>\n"
            "    <div class=\"item\">\n"
            "      <div>\n"
            "        <div class=\"label\">Patrick Campbell's Value Metric Pricing</div>\n"
            "        <div class=\"subtext\">Monetization expands with customer consumption/value</div>\n"
            "      </div>\n"
            "      <input type=\"checkbox\" onchange=\"updateScore()\">\n"
            "    </div>\n"
            "  </div>\n"
            "  <script>\n"
            "    function updateScore() {\n"
            "      const checkboxes = document.querySelectorAll('input[type=\"checkbox\"]');\n"
            "      let checked = 0;\n"
            "      checkboxes.forEach(c => { if (c.checked) checked++; });\n"
            "      const pct = Math.round((checked / checkboxes.length) * 100);\n"
            "      document.getElementById('score-display').innerText = pct + '%';\n"
            "    }\n"
            "  </script>\n"
            "</body>\n"
            "</html>\n"
            "```"
        )

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "provider": "mock",
            "model": self.model_name,
            "message": "Deterministic test & fallback provider operational",
        }
