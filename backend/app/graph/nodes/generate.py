from __future__ import annotations

import time

from app.model_adapter import OllamaAdapter

DEFAULT_LINE = "Aye. The old mine north of town had ore before the cave-in."


def generate_draft(state: dict, model_adapter: OllamaAdapter | None = None) -> dict:
    if model_adapter is None:
        return {"draft_line": DEFAULT_LINE, "emotion": "neutral", "model_latency_ms": 0.0}

    start = time.perf_counter()
    draft = model_adapter.generate_text(state["prompt"], temperature=0.2, max_tokens=140).strip()
    model_latency_ms = round((time.perf_counter() - start) * 1000, 2)
    if not draft:
        draft = DEFAULT_LINE
    return {"draft_line": draft, "emotion": "neutral", "model_latency_ms": model_latency_ms}
