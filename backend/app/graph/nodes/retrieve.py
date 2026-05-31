from __future__ import annotations

from app.lore_store import LoreStore


def retrieve_lore(state: dict, lore_store: LoreStore | None = None) -> dict:
    request = state["request"]
    if lore_store is None:
        return {"lore_chunks": []}

    chunks = lore_store.retrieve(
        npc_id=request["npc_id"],
        location=request["location"],
        query=request["player_line"],
        top_k=3,
    )
    return {
        "lore_chunks": [chunk.__dict__ for chunk in chunks],
    }
