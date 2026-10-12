"""Dedicated Ship 30 for 30 Essay Generation Skill."""

from typing import List, Dict, Any
from app.skills.base_skill import BaseSkill, SkillInput, SkillOutput
from app.retrieval.index import global_index
from app.retrieval.sources import build_citations
from app.services.provider_factory import provider_factory
from app.services.base_provider import ChatMessage
from app.core.config import settings
from app.core.logging import logger


SHIP_30_WRITING_PRINCIPLES = """
SHIP 30 FOR 30 WRITING PRINCIPLES (Nicolas Cole & Dickie Bush Framework):
1. THE IRRESISTIBLE HOOK:
   - Compelling Headline stating a clear tension or counterintuitive truth.
   - Opening 1-2 punchy lines that draw the reader in immediately. Avoid boring introductions.
2. ONE CORE THESIS:
   - Ground the essay in one central dilemma (e.g. why acquisition fails without retention, or how PMF is engineered).
3. VISUAL ARCHITECTURE & CADENCE:
   - Alternate paragraph lengths (single-sentence declarations, 2-3 sentence explanations).
   - Use Markdown H2 headers (`##`) for major milestones.
   - Use bullet points and markdown tables for high-density comparisons.
   - Use selective bold emphasis on key principles so a skimmer gets 80% of the value in 45 seconds.
4. GROUNDED EVIDENCE:
   - Incorporate exact frameworks, names, and metrics from Lenny's transcripts (Rahul Vohra's 40% rule, Elena Verna's Time-to-Aha, Brian Balfour's loops, Patrick Campbell's 11.1% monetization leverage, Shreyas Doshi's LNO).
   - Never fabricate anecdotes.
5. SPECIFIC EXECUTIVE TAKEAWAY:
   - Conclude with an actionable, bulleted 3-part framework or checklist the reader can apply tomorrow.
6. TARGET LENGTH:
   - Produce a thorough, high-utility longform essay of approximately 1,000 to 1,300 words.
"""


class Ship30Skill(BaseSkill):
    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        query = skill_input.user_message

        # 1. Retrieve grounded source material
        retrieved = global_index.retrieve(
            query=query,
            top_k=5,
            similarity_threshold=0.35,  # wider net for rich essay material
        )

        citations = build_citations(retrieved)

        # 2. Build context from transcript chunks
        context_blocks = []
        for idx, (chunk, score) in enumerate(retrieved, 1):
            context_blocks.append(
                f"[Source: {chunk.episode_title} | Guest: {chunk.guest_name}]\n{chunk.content}"
            )
        context_str = "\n\n---\n\n".join(context_blocks)

        system_prompt = (
            "You are an elite Product & Growth Ghostwriter specializing in the 'Ship 30 for 30' methodology.\n"
            f"{SHIP_30_WRITING_PRINCIPLES}\n\n"
            "STRICT GROUNDING REQUIREMENT:\n"
            "The essay must be derived strictly from the following transcripts from Lenny's Podcast. "
            "Do NOT invent quotes or make unsupported claims.\n\n"
            f"=== GROUNDED TRANSCRIPTS ===\n{context_str}\n=== END GROUNDED TRANSCRIPTS ==="
        )

        user_prompt = (
            f"Write a publishing-ready, Ship 30 for 30-style longform essay (~1,250 words) based on the following user prompt:\n\n"
            f"Prompt: {query}\n\n"
            "Ensure the essay includes:\n"
            "1. An irresistible hook and headline\n"
            "2. Clear narrative progression through numbered sections\n"
            "3. Skimmable formatting with bolded principles, bullet points, and high-impact takeaways\n"
            "4. Verifiable references to Lenny's podcast guests and their specific frameworks\n"
            "5. An actionable executive checklist at the end."
        )

        messages = [ChatMessage(role="user", content=user_prompt)]

        provider = provider_factory.get_provider(
            override_provider=skill_input.active_provider,
            override_model=skill_input.active_model,
        )

        try:
            llm_res = await provider.generate(messages, system_prompt=system_prompt)
            essay_content = llm_res.content
            meta = {
                "provider": llm_res.provider,
                "model": llm_res.model,
                "latency_ms": llm_res.latency_ms,
                "is_fallback": llm_res.is_fallback,
                "word_count": len(essay_content.split()),
            }
        except Exception as exc:
            logger.warning(f"Provider failed for Ship 30 essay ({exc}). Falling back to mock generator...")
            if settings.ALLOW_MOCK_FALLBACK:
                mock_prov = provider_factory.get_provider(override_provider="mock")
                llm_res = await mock_prov.generate(messages, system_prompt=system_prompt)
                essay_content = llm_res.content
                meta = {
                    "provider": "mock",
                    "model": mock_prov.model_name,
                    "latency_ms": llm_res.latency_ms,
                    "is_fallback": True,
                    "word_count": len(essay_content.split()),
                }
            else:
                raise exc

        # Also create a Markdown artifact representation for the Artifact Viewer!
        first_line = essay_content.strip().split("\n")[0].replace("#", "").strip()
        artifact_title = first_line if first_line else "Ship 30 for 30 Essay"

        artifact_data = {
            "artifact_type": "markdown",
            "title": artifact_title,
            "content": essay_content,
            "meta_info": {"word_count": len(essay_content.split()), "skill": "ship30"},
        }

        return SkillOutput(
            content=essay_content,
            intent="ship30_essay",
            citations=citations,
            artifacts=[artifact_data],
            suggested_follow_ups=[
                "Create an interactive HTML framework to calculate these metrics.",
                "How do you operationalize this checklist across a 20-person product team?",
                "What did Shreyas Doshi recommend regarding North Star counter-metrics?",
            ],
            is_grounded=True,
            meta_info=meta,
        )
