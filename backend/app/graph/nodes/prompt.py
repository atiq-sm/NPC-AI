from __future__ import annotations


def build_prompt(state: dict) -> dict:
    request = state["request"]
    lore_lines = [chunk["text"] for chunk in state.get("lore_chunks", [])]
    lore_block = "\n".join(f"- {line}" for line in lore_lines) if lore_lines else "- No lore found"

    prompt = (
        f"You are NPC {request['npc_id']}. Respond in 1-3 fantasy grounded sentences.\n"
        f"Player: {request['player_name']}\n"
        f"Location: {request['location']}\n"
        f"Time: {request['time_of_day']}\n"
        f"Player line: {request['player_line']}\n"
        f"Lore:\n{lore_block}\n"
        "Avoid modern terms and fourth-wall references."
    )
    return {"prompt": prompt}
