from __future__ import annotations


ALLOWED_EFFECTS = {
    "set_flag",
    "reveal_map_marker",
    "adjust_disposition",
    "start_quest",
    "play_emotion",
}


def extract_game_effects(state: dict) -> dict:
    request = state["request"]
    effects: list[dict] = []

    if (
        request["npc_id"] == "blacksmith_aldric"
        and state.get("intent") in {"ask_quest", "ask_location"}
        and "find_iron_ore" not in request["active_quests"]
    ):
        effects.append(
            {
                "type": "reveal_map_marker",
                "payload": {"marker_id": "iron_mines"},
            }
        )

    filtered = [effect for effect in effects if effect.get("type") in ALLOWED_EFFECTS]
    return {"game_effects": filtered}
