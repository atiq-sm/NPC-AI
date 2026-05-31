from __future__ import annotations

import warnings
import sqlite3
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.graph.nodes.classify import classify_intent
from app.graph.nodes.effects import extract_game_effects
from app.graph.nodes.fallback import fallback_response
from app.graph.nodes.format import format_output
from app.graph.nodes.generate import generate_draft
from app.graph.nodes.prompt import build_prompt
from app.graph.nodes.repair import repair_prompt
from app.graph.nodes.retrieve import retrieve_lore
from app.graph.nodes.validate import validate_response
from app.graph.state import DialogueState


def _after_classify(state: dict) -> str:
    return "retrieve_lore" if state.get("needs_lore") else "build_prompt"


def _after_validate(state: dict) -> str:
    status = state.get("validation_status", "valid")
    if status == "valid":
        return "extract_game_effects"
    if status == "retry":
        return "repair_prompt"
    return "fallback_response"


def create_checkpointer(sqlite_path: str | None = None):
    if not sqlite_path:
        return MemorySaver()

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver

        connection = sqlite3.connect(sqlite_path, check_same_thread=False)
        saver = SqliteSaver(connection)
        saver.setup()
        return saver
    except Exception as exc:
        warnings.warn(
            "SQLite checkpointing requested but langgraph-checkpoint-sqlite is unavailable; "
            "falling back to in-memory checkpoints. Install backend dependencies to persist state. "
            f"Original error: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return MemorySaver()


def build_graph(
    *,
    lore_store: Any | None = None,
    model_adapter: Any | None = None,
    checkpointer: Any | None = None,
):
    graph = StateGraph(DialogueState)

    graph.add_node("classify_intent", lambda state: classify_intent(state, model_adapter=model_adapter))
    graph.add_node("retrieve_lore", lambda state: retrieve_lore(state, lore_store=lore_store))
    graph.add_node("build_prompt", build_prompt)
    graph.add_node("generate_draft", lambda state: generate_draft(state, model_adapter=model_adapter))
    graph.add_node("validate_response", validate_response)
    graph.add_node("repair_prompt", repair_prompt)
    graph.add_node("fallback_response", fallback_response)
    graph.add_node("extract_game_effects", extract_game_effects)
    graph.add_node("format_output", format_output)

    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges("classify_intent", _after_classify)
    graph.add_edge("retrieve_lore", "build_prompt")
    graph.add_edge("build_prompt", "generate_draft")
    graph.add_edge("generate_draft", "validate_response")
    graph.add_conditional_edges(
        "validate_response",
        _after_validate,
        {
            "extract_game_effects": "extract_game_effects",
            "repair_prompt": "repair_prompt",
            "fallback_response": "fallback_response",
        },
    )
    graph.add_edge("repair_prompt", "generate_draft")
    graph.add_edge("fallback_response", "format_output")
    graph.add_edge("extract_game_effects", "format_output")
    graph.add_edge("format_output", END)

    return graph.compile(checkpointer=checkpointer or create_checkpointer())
