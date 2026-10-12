"""Base class for agent skills."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.session import CitationSchema
from app.schemas.chat import ArtifactSummary


class SkillInput(BaseModel):
    user_message: str
    session_id: str
    history: List[Dict[str, str]] = []
    active_provider: str
    active_model: str


class SkillOutput(BaseModel):
    content: str
    intent: str
    citations: List[CitationSchema] = []
    artifacts: List[Dict[str, Any]] = []
    suggested_follow_ups: List[str] = []
    is_grounded: bool = True
    meta_info: Dict[str, Any] = {}


class BaseSkill(ABC):
    @abstractmethod
    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        """Executes the specific skill and returns structured results."""
        pass
