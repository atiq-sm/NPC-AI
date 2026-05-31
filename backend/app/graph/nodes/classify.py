from __future__ import annotations

KEYWORDS = {
    "ask_quest": {"quest", "job", "work", "help"},
    "ask_location": {"where", "find", "located", "mine", "ore"},
    "smalltalk": {"hello", "hi", "weather", "how"},
}


def classify_intent(state: dict) -> dict:
    player_line = state["request"]["player_line"].lower()

    for intent, words in KEYWORDS.items():
        if any(word in player_line for word in words):
            needs_lore = intent in {"ask_quest", "ask_location"}
            return {"intent": intent, "needs_lore": needs_lore, "entities": {}}

    return {"intent": "unknown", "needs_lore": False, "entities": {}}
