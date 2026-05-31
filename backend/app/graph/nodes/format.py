from __future__ import annotations


def format_output(state: dict) -> dict:
    request = state["request"]
    output = {
        "line": state.get("draft_line", ""),
        "emotion": state.get("emotion", "neutral"),
        "game_effects": state.get("game_effects", []),
        "debug": {
            "intent": state.get("intent", "unknown"),
            "retry_count": state.get("retry_count", 0),
            "lore_chunks_used": len(state.get("lore_chunks", [])),
            "validation_errors": state.get("validation_errors", []),
            "dropped_effects": state.get("dropped_effects", []),
            "model_latency_ms": state.get("model_latency_ms", 0.0),
        },
    }
    return {
        "output": output,
        "history": [
            {"role": "player", "content": request["player_line"]},
            {"role": "npc", "content": output["line"]},
        ],
    }
