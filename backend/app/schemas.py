from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class DialogueTurnRequest(BaseModel):
    thread_id: str
    npc_id: str
    player_line: str
    player_name: str
    location: str
    active_quests: list[str] = Field(default_factory=list)
    inventory_flags: list[str] = Field(default_factory=list)
    npc_disposition: float = 0.0
    time_of_day: str = "day"


class GameEffect(BaseModel):
    type: Literal[
        "set_flag",
        "reveal_map_marker",
        "adjust_disposition",
        "start_quest",
        "play_emotion",
    ]
    payload: dict[str, Any] = Field(default_factory=dict)


class DialogueDebug(BaseModel):
    intent: str = "unknown"
    retry_count: int = 0
    lore_chunks_used: int = 0
    validation_errors: list[str] = Field(default_factory=list)


class DialogueTurnResponse(BaseModel):
    line: str
    emotion: str = "neutral"
    game_effects: list[GameEffect] = Field(default_factory=list)
    debug: DialogueDebug
