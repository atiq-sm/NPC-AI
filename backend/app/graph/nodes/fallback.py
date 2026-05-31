from __future__ import annotations

import json
from pathlib import Path


def fallback_response(state: dict) -> dict:
    request = state["request"]
    fallback_path = Path(__file__).resolve().parents[2] / "fallbacks" / f"{request['npc_id']}.json"
    line = "Best ask me again in a moment."
    if fallback_path.exists():
        lines = json.loads(fallback_path.read_text(encoding="utf-8")).get("lines", [])
        if lines:
            line = lines[0]
    return {"draft_line": line, "emotion": "neutral", "game_effects": []}
