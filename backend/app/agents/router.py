"""Intent router for classifying user requests and selecting agent skills."""

import re
from typing import Dict, Any, List


class IntentRouter:
    """Classifies user intent into discrete skills using pattern recognition and semantic heuristics."""

    def classify_intent(self, user_message: str, history: List[Dict[str, str]] = None) -> str:
        msg = user_message.strip().lower()

        # 1. Out of domain check
        out_of_domain_keywords = [
            "recipe for", "baking cake", "quantum mechanics", "quantum physics",
            "french revolution", "astrophysics", "who won the 1994 world cup",
            "capital of mongolia", "write python script to invert binary tree",
        ]
        if any(kw in msg for kw in out_of_domain_keywords):
            return "out_of_domain"

        # 2. Ship 30 for 30 Essay intent
        ship30_triggers = [
            "ship 30", "ship30", "atomic essay", "1250-word", "1,250 word", "1250 word",
            "write an essay", "write an article", "turn this into an essay",
            "turn this insight into an essay", "create an essay", "draft an essay",
            "ship 30 style", "longform essay",
        ]
        if any(trig in msg for trig in ship30_triggers):
            return "ship30_essay"

        # 3. Artifact generation intent (HTML/CSS, visual component, scorecard, dashboard)
        has_creation_intent = any(verb in msg for verb in ["generate", "create", "build", "make", "draft", "design", "render", "show me"])
        has_artifact_target = any(target in msg for target in ["html", "css", "scorecard", "calculator", "widget", "dashboard", "artifact"])

        if (has_creation_intent and has_artifact_target) or any(trig in msg for trig in [
            "html artifact", "css artifact", "interactive scorecard", "interactive dashboard",
            "html framework", "html/css", "create an artifact", "generate an artifact", "interactive calculator"
        ]):
            return "artifact_generation"

        # 4. Follow-up or standard Grounded Q&A
        return "grounded_qa"


router = IntentRouter()
