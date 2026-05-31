from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from app.model_adapter import OllamaAdapter

KEYWORDS = {
    "ask_quest": {"quest", "job", "work", "help"},
    "ask_location": {"where", "find", "located", "mine", "ore"},
    "smalltalk": {"hello", "hi", "weather", "how"},
}

Intent = Literal["ask_quest", "ask_location", "smalltalk", "unknown"]


class IntentClassification(BaseModel):
    intent: Intent = "unknown"
    needs_lore: bool = False
    entities: dict[str, Any] = Field(default_factory=dict)


def _heuristic_classify(player_line: str) -> dict:
    player_line = player_line.lower()
    for intent, words in KEYWORDS.items():
        if any(word in player_line for word in words):
            needs_lore = intent in {"ask_quest", "ask_location"}
            return {"intent": intent, "needs_lore": needs_lore, "entities": {}}

    return {"intent": "unknown", "needs_lore": False, "entities": {}}


def classify_intent(state: dict, model_adapter: OllamaAdapter | None = None) -> dict:
    player_line = state["request"]["player_line"].lower()
    if model_adapter is None:
        return _heuristic_classify(player_line)

    prompt = (
        "Classify this NPC dialogue player line into strict JSON.\n"
        "Allowed intents: ask_quest, ask_location, smalltalk, unknown.\n"
        "Set needs_lore true only when lore is needed to answer.\n"
        f"Player line: {state['request']['player_line']}"
    )
    try:
        result = model_adapter.generate_json(prompt, IntentClassification, retries=1)
        classified = IntentClassification.model_validate(result).model_dump()
    except (AttributeError, ValidationError, TypeError, ValueError):
        classified = _heuristic_classify(player_line)

    if classified["intent"] == "unknown":
        heuristic = _heuristic_classify(player_line)
        if heuristic["intent"] != "unknown":
            return heuristic
    return classified
