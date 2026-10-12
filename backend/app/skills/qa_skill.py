"""Grounded Question Answering skill."""

from typing import List
from app.skills.base_skill import BaseSkill, SkillInput, SkillOutput
from app.retrieval.index import global_index
from app.retrieval.sources import build_citations
from app.services.provider_factory import provider_factory
from app.services.base_provider import ChatMessage
from app.core.config import settings
from app.core.logging import logger


class GroundedQASkill(BaseSkill):
    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        query = skill_input.user_message

        # 1. Retrieve relevant transcript chunks
        retrieved = global_index.retrieve(
            query=query,
            top_k=settings.TOP_K_CHUNKS,
            similarity_threshold=settings.SIMILARITY_THRESHOLD,
        )

        citations = build_citations(retrieved)

        # 2. Check if retrieval found sufficient grounding
        if not retrieved:
            # Low confidence or out-of-domain: strictly refuse without hallucinating
            refusal_text = (
                "I searched the available transcript knowledge base for Lenny's Podcast, "
                "but I could not find information supporting this topic. "
                "The available transcripts primarily cover product-market fit (Rahul Vohra), "
                "product-led growth & onboarding (Elena Verna), growth loops (Brian Balfour), "
                "PM prioritization & metrics (Shreyas Doshi), and SaaS pricing (Patrick Campbell).\n\n"
                "Please ask a question related to these growth and product topics."
            )
            return SkillOutput(
                content=refusal_text,
                intent="grounded_qa_unsupported",
                citations=[],
                suggested_follow_ups=[
                    "How does Rahul Vohra measure Product-Market Fit?",
                    "What does Elena Verna recommend for onboarding and retention?",
                    "How does Brian Balfour define Growth Loops vs. Funnels?",
                ],
                is_grounded=False,
                meta_info={"reason": "no_chunks_above_threshold"},
            )

        # 3. Assemble Grounded Context
        context_blocks = []
        for idx, (chunk, score) in enumerate(retrieved, 1):
            context_blocks.append(
                f"[Source {idx} | Episode: {chunk.episode_title} | Guest: {chunk.guest_name} | Match Score: {score:.2f}]\n"
                f"{chunk.content}"
            )
        context_str = "\n\n---\n\n".join(context_blocks)

        system_prompt = (
            "You are 'The Lenny Growth Assistant', an executive product and growth copilot. "
            "You answer product management and growth questions strictly grounded in the provided transcripts from Lenny's Podcast.\n\n"
            "STRICT GROUNDING RULES:\n"
            "1. Answer ONLY using the facts, frameworks, and quotes directly mentioned in the TRANSCRIPT CONTEXT below.\n"
            "2. Do NOT invent quotes, episodes, or metrics from general AI knowledge.\n"
            "3. Explicitly cite the guest's name and episode when stating key frameworks or numbers.\n"
            "4. Format your answer with clean Markdown headers, bullet points, and selective bold emphasis for skimmability.\n"
            "5. If a detail is not supported by the transcript context, explicitly state that the transcript does not provide it.\n\n"
            f"=== TRANSCRIPT CONTEXT ===\n{context_str}\n=== END TRANSCRIPT CONTEXT ==="
        )

        # Build conversation history
        messages: List[ChatMessage] = []
        for h in skill_input.history[-4:]:  # last 4 turns for context
            messages.append(ChatMessage(role=h["role"], content=h["content"]))
        messages.append(ChatMessage(role="user", content=query))

        # 4. Invoke LLM provider
        provider = provider_factory.get_provider(
            override_provider=skill_input.active_provider,
            override_model=skill_input.active_model,
        )

        try:
            llm_res = await provider.generate(messages, system_prompt=system_prompt)
            content = llm_res.content
            meta = {
                "provider": llm_res.provider,
                "model": llm_res.model,
                "latency_ms": llm_res.latency_ms,
                "is_fallback": llm_res.is_fallback,
            }
        except Exception as exc:
            logger.warning(f"Active provider {provider.model_name} failed ({exc}). Checking fallback...")
            if settings.ALLOW_MOCK_FALLBACK:
                mock_prov = provider_factory.get_provider(override_provider="mock")
                llm_res = await mock_prov.generate(messages, system_prompt=system_prompt)
                content = llm_res.content
                meta = {
                    "provider": "mock",
                    "model": mock_prov.model_name,
                    "latency_ms": llm_res.latency_ms,
                    "is_fallback": True,
                    "fallback_reason": str(exc),
                }
            else:
                raise exc

        # 5. Formulate logical follow-up questions
        follow_ups = self._generate_follow_ups(query)

        return SkillOutput(
            content=content,
            intent="grounded_qa",
            citations=citations,
            suggested_follow_ups=follow_ups,
            is_grounded=True,
            meta_info=meta,
        )

    def _generate_follow_ups(self, query: str) -> List[str]:
        q = query.lower()
        if "rahul" in q or "pmf" in q or "superhuman" in q:
            return [
                "What metrics should I track to know if PMF is improving?",
                "How do you segment 'High-Expectation Customers' in B2B?",
                "Turn this PMF engine into a Ship 30 for 30 essay.",
            ]
        elif "elena" in q or "verna" in q or "onboarding" in q:
            return [
                "How do you calculate Time to Aha! in onboarding?",
                "When should a startup pick Freemium over a Free Trial?",
                "Generate an interactive HTML scorecard for our onboarding funnel.",
            ]
        elif "brian" in q or "balfour" in q or "loop" in q:
            return [
                "What is the difference between Viral Loops and Content Loops?",
                "How do you test Product-Channel Fit before scaling spend?",
                "Create a markdown framework comparing Funnels vs Loops.",
            ]
        elif "pricing" in q or "patrick" in q or "campbell" in q:
            return [
                "Why does per-seat pricing damage viral expansion?",
                "How do you discover your product's true Value Metric?",
                "Write an atomic essay on the 4x pricing advantage.",
            ]
        return [
            "How does this connect to retention metrics?",
            "What did other guests on Lenny's podcast say about this?",
            "Turn these takeaways into a Ship 30 for 30 essay.",
        ]
