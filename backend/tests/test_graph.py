from pathlib import Path

from app.graph.builder import build_graph
from app.lore_store import LoreStore
from app.schemas import DialogueTurnRequest


class FakeAdapter:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 160) -> str:
        if self.outputs:
            return self.outputs.pop(0)
        return "Aye. The old mine north of town had ore before the cave-in."


def _make_state(thread_id: str, line: str) -> dict:
    return {
        "request": DialogueTurnRequest(
            thread_id=thread_id,
            npc_id="blacksmith_aldric",
            player_line=line,
            player_name="Aria",
            location="village_forge",
            active_quests=[],
            inventory_flags=[],
            npc_disposition=0.3,
            time_of_day="morning",
        ).model_dump(),
        "retry_count": 0,
    }


def test_retry_then_fallback_after_cap() -> None:
    graph = build_graph(
        lore_store=LoreStore(Path(__file__).resolve().parents[1] / "app" / "lore" / "index.json"),
        model_adapter=FakeAdapter(["As an AI, I cannot do that."] * 3),
    )
    result = graph.invoke(_make_state(thread_id="t1", line="Where can I find iron ore?"), config={"configurable": {"thread_id": "t1"}})
    assert result["retry_count"] == 2
    assert result["output"]["line"]
    assert result["output"]["debug"]["validation_errors"]


def test_effect_allowlist_reveals_marker() -> None:
    graph = build_graph(
        lore_store=LoreStore(Path(__file__).resolve().parents[1] / "app" / "lore" / "index.json"),
        model_adapter=FakeAdapter(["Check the old mine north of town for iron ore."]),
    )
    result = graph.invoke(_make_state(thread_id="t2", line="Do you have any work for me?"), config={"configurable": {"thread_id": "t2"}})
    effects = result["output"]["game_effects"]
    assert effects
    assert effects[0]["type"] == "reveal_map_marker"
