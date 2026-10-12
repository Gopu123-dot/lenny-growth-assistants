"""Automated tests for agent intent routing."""

from app.agents.router import router


def test_routing_grounded_qa():
    intent = router.classify_intent("How does Elena Verna define the Time to Aha moment in onboarding?")
    assert intent == "grounded_qa"


def test_routing_ship30_essay():
    intent = router.classify_intent("Write a Ship 30 for 30 essay on why retention breaks before acquisition.")
    assert intent == "ship30_essay"

    intent2 = router.classify_intent("Turn this insight into a 1250-word atomic essay.")
    assert intent2 == "ship30_essay"


def test_routing_artifact_generation():
    intent = router.classify_intent("Generate an interactive HTML scorecard for evaluating onboarding friction.")
    assert intent == "artifact_generation"

    intent2 = router.classify_intent("Create an HTML/CSS dashboard based on this framework.")
    assert intent2 == "artifact_generation"


def test_routing_out_of_domain():
    intent = router.classify_intent("Explain the French Revolution and the storming of the Bastille.")
    assert intent == "out_of_domain"
