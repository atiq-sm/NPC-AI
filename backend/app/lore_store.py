from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoreChunk:
    text: str
    npc_id: str | None = None
    location: str | None = None
    quest_id: str | None = None
    spoiler_level: int = 0
    source_path: str = ""


class LoreStore:
    def __init__(self, index_path: Path) -> None:
        self.index_path = index_path
        self.chunks = self._load()

    def _load(self) -> list[LoreChunk]:
        if not self.index_path.exists():
            return []
        raw = json.loads(self.index_path.read_text(encoding="utf-8"))
        return [LoreChunk(**item) for item in raw]

    def retrieve(self, npc_id: str, location: str, query: str, top_k: int = 3) -> list[LoreChunk]:
        terms = set(query.lower().split())

        def score(chunk: LoreChunk) -> int:
            if chunk.npc_id not in (None, npc_id):
                return -1
            base = 2 if chunk.location in (None, location) else 0
            overlap = sum(1 for token in terms if token in chunk.text.lower())
            return base + overlap

        ranked = [chunk for chunk in self.chunks if score(chunk) >= 0]
        ranked.sort(key=score, reverse=True)
        return ranked[:top_k]
