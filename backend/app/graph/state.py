from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class DialogueState(TypedDict, total=False):
    request: dict[str, Any]
    history: Annotated[list[dict[str, str]], operator.add]
    intent: str
    entities: dict[str, Any]
    needs_lore: bool
    lore_chunks: list[dict[str, Any]]
    prompt: str
    draft_line: str
    emotion: str
    game_effects: list[dict[str, Any]]
    dropped_effects: list[dict[str, Any]]
    retry_count: int
    validation_errors: list[str]
    validation_status: str
    model_latency_ms: float
    output: dict[str, Any]
