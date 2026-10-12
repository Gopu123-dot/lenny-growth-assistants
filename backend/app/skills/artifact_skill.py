"""Dedicated Artifact Generation Skill for Markdown and HTML/CSS components."""

import re
from typing import List, Dict, Any, Tuple
from app.skills.base_skill import BaseSkill, SkillInput, SkillOutput
from app.retrieval.index import global_index
from app.retrieval.sources import build_citations
from app.services.provider_factory import provider_factory
from app.services.base_provider import ChatMessage
from app.core.config import settings
from app.core.logging import logger


class ArtifactSkill(BaseSkill):
    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        query = skill_input.user_message

        # 1. Retrieve grounded material
        retrieved = global_index.retrieve(
            query=query,
            top_k=4,
            similarity_threshold=0.35,
        )

        citations = build_citations(retrieved)

        context_blocks = []
        for idx, (chunk, score) in enumerate(retrieved, 1):
            context_blocks.append(
                f"[Source: {chunk.episode_title} | Guest: {chunk.guest_name}]\n{chunk.content}"
            )
        context_str = "\n\n---\n\n".join(context_blocks)

        is_html_requested = any(kw in query.lower() for kw in ["html", "widget", "scorecard", "calculator", "dashboard"])
        artifact_type = "html" if is_html_requested else "markdown"

        system_prompt = (
            "You are 'The Lenny Growth Assistant' Artifact Engineer.\n"
            "Your job is to generate high-utility, standalone product and growth artifacts grounded in Lenny's Podcast knowledge.\n\n"
            "GROUNDING CONTEXT:\n"
            f"{context_str}\n\n"
            "REQUIREMENTS:\n"
            "1. If HTML is requested: Generate a complete, standalone, responsive HTML5 document with embedded <style> and lightweight interactive <script>.\n"
            "   - Use clean, modern dark-mode styling (slate backgrounds, indigo/emerald accents).\n"
            "   - Enclose the entire HTML document in a single ```html ``` code fence.\n"
            "2. If Markdown is requested: Generate a structured executive framework or memo with tables and checklists.\n"
            "   - Enclose in a ```markdown ``` code fence.\n"
            "3. Ground all formulas, benchmarks, and checklist items in the provided transcript context."
        )

        user_prompt = f"Please generate a complete {artifact_type} artifact for the following request:\n{query}"
        messages = [ChatMessage(role="user", content=user_prompt)]

        provider = provider_factory.get_provider(
            override_provider=skill_input.active_provider,
            override_model=skill_input.active_model,
        )

        try:
            llm_res = await provider.generate(messages, system_prompt=system_prompt)
            raw_content = llm_res.content
            meta = {
                "provider": llm_res.provider,
                "model": llm_res.model,
                "latency_ms": llm_res.latency_ms,
                "is_fallback": llm_res.is_fallback,
            }
        except Exception as exc:
            logger.warning(f"Provider failed for artifact generation ({exc}). Falling back...")
            if settings.ALLOW_MOCK_FALLBACK:
                mock_prov = provider_factory.get_provider(override_provider="mock")
                llm_res = await mock_prov.generate(messages, system_prompt=system_prompt)
                raw_content = llm_res.content
                meta = {
                    "provider": "mock",
                    "model": mock_prov.model_name,
                    "latency_ms": llm_res.latency_ms,
                    "is_fallback": True,
                }
            else:
                raise exc

        # Extract code and title
        artifact_code, detected_type, title = self._extract_artifact_data(raw_content, artifact_type)

        chat_explanation = (
            f"I have generated the requested **{title}** grounded in Lenny's transcript knowledge base.\n\n"
            f"You can view and interact with this artifact directly in the **Artifact Viewer** panel on the right."
        )

        artifact_data = {
            "artifact_type": detected_type,
            "title": title,
            "content": artifact_code,
            "meta_info": {"generated_from_prompt": query, "format": detected_type},
        }

        return SkillOutput(
            content=chat_explanation,
            intent="artifact_generation",
            citations=citations,
            artifacts=[artifact_data],
            suggested_follow_ups=[
                "How can we modify the weights in this framework?",
                "Turn this framework into a Ship 30 for 30 essay.",
                "What did Elena Verna or Rahul Vohra say about these specific metrics?",
            ],
            is_grounded=True,
            meta_info=meta,
        )

    def _extract_artifact_data(self, text: str, fallback_type: str) -> Tuple[str, str, str]:
        """Extracts code block, type, and title from model output."""
        html_match = re.search(r"```html\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if html_match:
            code = html_match.group(1).strip()
            title_match = re.search(r"<title>(.*?)</title>", code, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "Growth Component"
            return code, "html", title

        md_match = re.search(r"```markdown\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if md_match:
            code = md_match.group(1).strip()
            first_line = code.split("\n")[0].replace("#", "").strip()
            return code, "markdown", first_line or "Growth Strategy Memo"

        # Fallback if no fence
        return text, fallback_type, "Generated Growth Artifact"
