from __future__ import annotations

import json
import re
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

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", text.lower()))

    def retrieve(self, npc_id: str, location: str, query: str, top_k: int = 3) -> list[LoreChunk]:
        terms = self._tokens(query)

        def score(chunk: LoreChunk) -> int:
            if chunk.npc_id not in (None, npc_id):
                return -1
            if chunk.location not in (None, location):
                return -1
            chunk_terms = self._tokens(chunk.text)
            metadata_bonus = 0
            if chunk.npc_id == npc_id:
                metadata_bonus += 3
            if chunk.location == location:
                metadata_bonus += 2
            if chunk.quest_id and chunk.quest_id in terms:
                metadata_bonus += 1
            overlap = len(terms & chunk_terms)
            return metadata_bonus + overlap

        ranked = [chunk for chunk in self.chunks if score(chunk) >= 0]
        ranked.sort(key=score, reverse=True)
        return ranked[:top_k]
