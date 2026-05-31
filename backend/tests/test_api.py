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
