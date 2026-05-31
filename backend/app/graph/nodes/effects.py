from __future__ import annotations


ALLOWED_EFFECTS = {
    "set_flag",
    "reveal_map_marker",
    "adjust_disposition",
    "start_quest",
    "play_emotion",
}
KNOWN_MARKERS = {"iron_mines"}
KNOWN_QUESTS = {"find_iron_ore"}


def validate_game_effects(effects: list[dict]) -> tuple[list[dict], list[dict]]:
    valid: list[dict] = []
    dropped: list[dict] = []

    for effect in effects:
        effect_type = effect.get("type")
        payload = effect.get("payload", {})
        if effect_type not in ALLOWED_EFFECTS or not isinstance(payload, dict):
            dropped.append(effect)
            continue
        if effect_type == "reveal_map_marker" and payload.get("marker_id") not in KNOWN_MARKERS:
            dropped.append(effect)
            continue
        if effect_type == "start_quest" and payload.get("quest_id") not in KNOWN_QUESTS:
            dropped.append(effect)
            continue
        if effect_type == "adjust_disposition" and not isinstance(payload.get("delta"), (int, float)):
            dropped.append(effect)
            continue
        if effect_type == "set_flag" and not isinstance(payload.get("flag"), str):
            dropped.append(effect)
            continue
        if effect_type == "play_emotion" and not isinstance(payload.get("emotion"), str):
            dropped.append(effect)
            continue
        valid.append(effect)

    return valid, dropped


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

    filtered, dropped = validate_game_effects(effects)
    return {"game_effects": filtered, "dropped_effects": dropped}
