from __future__ import annotations

from typing import Any, TypedDict


class DialogueState(TypedDict, total=False):
    request: dict[str, Any]
    intent: str
    entities: dict[str, Any]
    needs_lore: bool
    lore_chunks: list[dict[str, Any]]
    prompt: str
    draft_line: str
    emotion: str
    game_effects: list[dict[str, Any]]
    retry_count: int
    validation_errors: list[str]
    validation_status: str
    output: dict[str, Any]
