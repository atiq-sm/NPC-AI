from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI

from app.graph.builder import build_graph, create_checkpointer
from app.lore_store import LoreStore
from app.model_adapter import OllamaAdapter
from app.schemas import DialogueTurnRequest, DialogueTurnResponse

app = FastAPI(title="NPC Dialogue Backend")

BASE_DIR = Path(__file__).resolve().parent
lore_store = LoreStore(BASE_DIR / "lore" / "index.json")
model_adapter = OllamaAdapter()
checkpointer = create_checkpointer(str(BASE_DIR / "dialogue_state.sqlite"))
dialogue_graph = build_graph(
    lore_store=lore_store,
    model_adapter=model_adapter,
    checkpointer=checkpointer,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/dialogue/turn", response_model=DialogueTurnResponse)
def dialogue_turn(payload: DialogueTurnRequest) -> DialogueTurnResponse:
    start = time.perf_counter()
    initial_state = {
        "request": payload.model_dump(),
        "retry_count": 0,
    }
    config = {"configurable": {"thread_id": payload.thread_id}}
    result = dialogue_graph.invoke(initial_state, config=config)
    result["output"]["debug"]["total_latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
    return DialogueTurnResponse.model_validate(result["output"])


@app.get("/dialogue/threads/{thread_id}/last")
def get_last_thread_state(thread_id: str) -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    state = dialogue_graph.get_state(config)
    if not state or not state.values:
        return {"thread_id": thread_id, "found": False}

    values = state.values
    return {
        "thread_id": thread_id,
        "found": True,
        "intent": values.get("intent", "unknown"),
        "retry_count": values.get("retry_count", 0),
        "lore_chunks_used": len(values.get("lore_chunks", [])),
        "line": values.get("draft_line", ""),
    }
