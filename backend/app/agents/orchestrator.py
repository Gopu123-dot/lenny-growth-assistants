"""Agent orchestrator coordinating session state, routing, skills, and persistence."""

import time
import uuid
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm import Session as SessionModel, Message as MessageModel, Citation as CitationModel, Artifact as ArtifactModel
from app.schemas.chat import ChatRequest, ChatResponse, ArtifactSummary
from app.schemas.session import CitationSchema
from app.agents.router import router
from app.skills.base_skill import SkillInput, SkillOutput
from app.skills.qa_skill import GroundedQASkill
from app.skills.ship30_skill import Ship30Skill
from app.skills.artifact_skill import ArtifactSkill
from app.services.provider_factory import provider_factory
from app.core.logging import logger


class AgentOrchestrator:
    def __init__(self):
        self.qa_skill = GroundedQASkill()
        self.ship30_skill = Ship30Skill()
        self.artifact_skill = ArtifactSkill()

    async def handle_chat(self, req: ChatRequest, db: AsyncSession) -> ChatResponse:
        start_time = time.perf_counter()

        # 1. Resolve or create Session
        session_id = req.session_id
        session_obj = None

        if session_id:
            res = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
            session_obj = res.scalar_one_or_none()

        if not session_obj:
            session_id = str(uuid.uuid4())
            provider = req.provider_override or provider_factory.active_provider_name
            model = req.model_override or provider_factory.active_model_name
            session_obj = SessionModel(
                id=session_id,
                title=req.message[:40] + ("..." if len(req.message) > 40 else ""),
                active_provider=provider,
                active_model=model,
            )
            db.add(session_obj)
            await db.flush()

        # 2. Fetch recent conversation history for session context (strict session isolation)
        hist_res = await db.execute(
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.asc())
        )
        existing_messages = hist_res.scalars().all()
        history_list = [{"role": m.role, "content": m.content} for m in existing_messages]

        # 3. Classify intent
        intent = router.classify_intent(req.message, history_list)
        logger.info(f"Intent classified as '{intent}' for session {session_id}")

        active_provider = req.provider_override or session_obj.active_provider
        active_model = req.model_override or session_obj.active_model

        skill_input = SkillInput(
            user_message=req.message,
            session_id=session_id,
            history=history_list,
            active_provider=active_provider,
            active_model=active_model,
        )

        # 4. Route to appropriate skill
        skill_output: SkillOutput
        if intent == "out_of_domain":
            skill_output = SkillOutput(
                content=(
                    "I searched the available transcript knowledge base for Lenny's Podcast, "
                    "but I could not find information supporting this topic. "
                    "I am strictly grounded in Lenny's interviews on product management, growth loops, "
                    "onboarding, retention, and SaaS pricing."
                ),
                intent="out_of_domain_refusal",
                citations=[],
                suggested_follow_ups=[
                    "What did Rahul Vohra say about Product-Market Fit?",
                    "How does Elena Verna recommend structuring onboarding?",
                    "What are Brian Balfour's Growth Loops?",
                ],
                is_grounded=False,
            )
        elif intent == "ship30_essay":
            skill_output = await self.ship30_skill.execute(skill_input)
        elif intent == "artifact_generation":
            skill_output = await self.artifact_skill.execute(skill_input)
        else:
            skill_output = await self.qa_skill.execute(skill_input)

        # 5. Persist User Message
        user_msg = MessageModel(
            session_id=session_id,
            role="user",
            content=req.message,
            meta_info={"intent": intent},
        )
        db.add(user_msg)
        await db.flush()

        # 6. Persist Assistant Message
        assistant_msg_id = str(uuid.uuid4())
        assistant_msg = MessageModel(
            id=assistant_msg_id,
            session_id=session_id,
            role="assistant",
            content=skill_output.content,
            meta_info={
                "intent": skill_output.intent,
                "provider": active_provider,
                "model": active_model,
                "is_grounded": skill_output.is_grounded,
                **skill_output.meta_info,
            },
        )
        db.add(assistant_msg)
        await db.flush()

        # 7. Persist Citations
        saved_citations: List[CitationSchema] = []
        for c in skill_output.citations:
            cit_record = CitationModel(
                message_id=assistant_msg_id,
                episode_title=c.episode_title,
                guest_name=c.guest_name,
                source_url=c.source_url,
                chunk_id=c.chunk_id,
                similarity_score=c.similarity_score,
                snippet=c.snippet,
            )
            db.add(cit_record)
            saved_citations.append(c)

        # 8. Persist Artifacts if generated
        artifact_summaries: List[ArtifactSummary] = []
        for art in skill_output.artifacts:
            art_id = str(uuid.uuid4())
            art_record = ArtifactModel(
                id=art_id,
                session_id=session_id,
                message_id=assistant_msg_id,
                artifact_type=art.get("artifact_type", "markdown"),
                title=art.get("title", "Growth Artifact"),
                content=art.get("content", ""),
                meta_info=art.get("meta_info", {}),
            )
            db.add(art_record)
            artifact_summaries.append(
                ArtifactSummary(
                    id=art_id,
                    artifact_type=art_record.artifact_type,
                    title=art_record.title,
                    preview_snippet=art_record.content[:100] + "...",
                )
            )

        # Update session title if first turn
        if len(existing_messages) == 0:
            session_obj.title = req.message[:45].strip()
        session_obj.updated_at = assistant_msg.created_at
        await db.commit()

        total_latency_ms = (time.perf_counter() - start_time) * 1000

        return ChatResponse(
            session_id=session_id,
            message_id=assistant_msg_id,
            role="assistant",
            content=skill_output.content,
            intent=skill_output.intent,
            citations=saved_citations,
            artifacts=artifact_summaries,
            suggested_follow_ups=skill_output.suggested_follow_ups,
            active_provider=active_provider,
            active_model=active_model,
            latency_ms=round(total_latency_ms, 2),
            is_grounded=skill_output.is_grounded,
        )


orchestrator = AgentOrchestrator()
