from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dialogue_turn_contract() -> None:
    payload = {
        "thread_id": "blacksmith_aldric_save001",
        "npc_id": "blacksmith_aldric",
        "player_line": "Do you know where I can find iron ore?",
        "player_name": "Aria",
        "location": "village_forge",
        "active_quests": [],
        "inventory_flags": ["has_pickaxe"],
        "npc_disposition": 0.3,
        "time_of_day": "morning",
    }

    response = client.post("/dialogue/turn", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"line", "emotion", "game_effects", "debug"}
    assert body["debug"]["intent"] in {"ask_quest", "ask_location", "unknown"}
    assert isinstance(body["game_effects"], list)
    assert isinstance(body["debug"]["total_latency_ms"], float)
    assert isinstance(body["debug"]["model_latency_ms"], float)
    assert "dropped_effects" in body["debug"]


def test_dialogue_turn_rejects_malformed_payload() -> None:
    response = client.post(
        "/dialogue/turn",
        json={
            "thread_id": "bad",
            "npc_id": "blacksmith_aldric",
        },
    )

    assert response.status_code == 422


def test_last_thread_state_is_summary_only() -> None:
    payload = {
        "thread_id": "summary_thread",
        "npc_id": "blacksmith_aldric",
        "player_line": "Do you know where I can find iron ore?",
        "player_name": "Aria",
        "location": "village_forge",
        "active_quests": [],
        "inventory_flags": ["has_pickaxe"],
        "npc_disposition": 0.3,
        "time_of_day": "morning",
    }

    client.post("/dialogue/turn", json=payload)
    response = client.get("/dialogue/threads/summary_thread/last")

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert "prompt" not in body
    assert body["history_turns"] >= 1
