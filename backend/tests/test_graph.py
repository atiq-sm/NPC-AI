from pathlib import Path

import pytest

from app.graph.builder import build_graph, create_checkpointer
from app.graph.nodes.effects import validate_game_effects
from app.lore_store import LoreStore
from app.schemas import DialogueTurnRequest


class FakeAdapter:
    def __init__(self, outputs: list[str], json_outputs: list[dict] | None = None) -> None:
        self.outputs = outputs
        self.json_outputs = json_outputs or []

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 160) -> str:
        if self.outputs:
            return self.outputs.pop(0)
        return "Aye. The old mine north of town had ore before the cave-in."

    def generate_json(self, prompt: str, schema_hint, retries: int = 1) -> dict:
        if self.json_outputs:
            return self.json_outputs.pop(0)
        return schema_hint.model_validate({}).model_dump()


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


def _lore_store() -> LoreStore:
    return LoreStore(Path(__file__).resolve().parents[1] / "app" / "lore" / "index.json")


def test_same_thread_preserves_history() -> None:
    graph = build_graph(
        lore_store=_lore_store(),
        model_adapter=FakeAdapter(
            [
                "Aye. The old mine north of town had ore before the cave-in.",
                "Bring a pickaxe if you value your hands.",
            ],
            [
                {"intent": "ask_location", "needs_lore": True, "entities": {}},
                {"intent": "smalltalk", "needs_lore": False, "entities": {}},
            ],
        ),
    )
    config = {"configurable": {"thread_id": "history-thread"}}

    graph.invoke(_make_state(thread_id="history-thread", line="Where can I find iron ore?"), config=config)
    result = graph.invoke(_make_state(thread_id="history-thread", line="Thanks, Aldric."), config=config)

    assert [entry["role"] for entry in result["history"]] == ["player", "npc", "player", "npc"]
    assert result["history"][0]["content"] == "Where can I find iron ore?"


def test_sqlite_checkpoint_creation_is_explicit(tmp_path: Path) -> None:
    try:
        checkpointer = create_checkpointer(str(tmp_path / "checkpoints.sqlite"))
    except RuntimeWarning:
        pytest.fail("create_checkpointer should warn and fall back, not raise")

    assert checkpointer is not None


def test_model_json_classifier_routes_to_lore() -> None:
    graph = build_graph(
        lore_store=_lore_store(),
        model_adapter=FakeAdapter(
            ["Aye. The old mine north of town had ore before the cave-in."],
            [{"intent": "ask_location", "needs_lore": True, "entities": {"resource": "iron ore"}}],
        ),
    )

    result = graph.invoke(
        _make_state(thread_id="json-classifier", line="Can you point me toward iron ore?"),
        config={"configurable": {"thread_id": "json-classifier"}},
    )

    assert result["intent"] == "ask_location"
    assert result["output"]["debug"]["lore_chunks_used"] > 0


def test_invalid_json_classifier_falls_back_to_heuristic() -> None:
    graph = build_graph(
        lore_store=_lore_store(),
        model_adapter=FakeAdapter(
            ["Aye. The old mine north of town had ore before the cave-in."],
            [{"intent": "not_real", "needs_lore": True, "entities": {}}],
        ),
    )

    result = graph.invoke(
        _make_state(thread_id="json-fallback", line="Where can I find iron ore?"),
        config={"configurable": {"thread_id": "json-fallback"}},
    )

    assert result["intent"] == "ask_location"


def test_retry_then_fallback_after_cap() -> None:
    graph = build_graph(
        lore_store=_lore_store(),
        model_adapter=FakeAdapter(
            ["As an AI, I cannot do that."] * 3,
            [{"intent": "ask_location", "needs_lore": True, "entities": {}}],
        ),
    )
    result = graph.invoke(_make_state(thread_id="t1", line="Where can I find iron ore?"), config={"configurable": {"thread_id": "t1"}})
    assert result["retry_count"] == 2
    assert result["output"]["line"]
    assert result["output"]["debug"]["validation_errors"]


def test_effect_allowlist_reveals_marker() -> None:
    graph = build_graph(
        lore_store=_lore_store(),
        model_adapter=FakeAdapter(
            ["Check the old mine north of town for iron ore."],
            [{"intent": "ask_quest", "needs_lore": True, "entities": {}}],
        ),
    )
    result = graph.invoke(_make_state(thread_id="t2", line="Do you have any work for me?"), config={"configurable": {"thread_id": "t2"}})
    effects = result["output"]["game_effects"]
    assert effects
    assert effects[0]["type"] == "reveal_map_marker"


def test_active_quest_suppresses_duplicate_marker() -> None:
    state = _make_state(thread_id="active-quest", line="Any work?")
    state["request"]["active_quests"] = ["find_iron_ore"]
    graph = build_graph(
        lore_store=_lore_store(),
        model_adapter=FakeAdapter(
            ["Check the old mine north of town for iron ore."],
            [{"intent": "ask_quest", "needs_lore": True, "entities": {}}],
        ),
    )

    result = graph.invoke(state, config={"configurable": {"thread_id": "active-quest"}})

    assert result["output"]["game_effects"] == []


def test_effect_validation_drops_unknown_and_malformed_payloads() -> None:
    valid, dropped = validate_game_effects(
        [
            {"type": "reveal_map_marker", "payload": {"marker_id": "iron_mines"}},
            {"type": "reveal_map_marker", "payload": {"marker_id": "secret_castle"}},
            {"type": "teleport", "payload": {"location": "old_mine"}},
        ]
    )

    assert valid == [{"type": "reveal_map_marker", "payload": {"marker_id": "iron_mines"}}]
    assert len(dropped) == 2


def test_unknown_game_context_id_triggers_fallback_after_retries() -> None:
    graph = build_graph(
        lore_store=_lore_store(),
        model_adapter=FakeAdapter(
            ["Take dragon_quest from the hidden marker."] * 3,
            [{"intent": "ask_quest", "needs_lore": True, "entities": {}}],
        ),
    )

    result = graph.invoke(_make_state(thread_id="bad-context", line="Any work?"), config={"configurable": {"thread_id": "bad-context"}})

    assert result["retry_count"] == 2
    assert "unknown_game_context_id" in result["output"]["debug"]["validation_errors"]
