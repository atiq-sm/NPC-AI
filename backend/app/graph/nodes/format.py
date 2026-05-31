from __future__ import annotations


def format_output(state: dict) -> dict:
    output = {
        "line": state.get("draft_line", ""),
        "emotion": state.get("emotion", "neutral"),
        "game_effects": state.get("game_effects", []),
        "debug": {
            "intent": state.get("intent", "unknown"),
            "retry_count": state.get("retry_count", 0),
            "lore_chunks_used": len(state.get("lore_chunks", [])),
            "validation_errors": state.get("validation_errors", []),
        },
    }
    return {"output": output}
