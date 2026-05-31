from __future__ import annotations

import argparse
import uuid

from app.main import dialogue_turn
from app.schemas import DialogueTurnRequest


def main() -> None:
    parser = argparse.ArgumentParser(description="NPC dialogue CLI harness")
    parser.add_argument("--npc", default="blacksmith_aldric")
    parser.add_argument("--location", default="village_forge")
    parser.add_argument("--player", default="Aria")
    parser.add_argument("--thread-id", default=None)
    args = parser.parse_args()

    thread_id = args.thread_id or f"{args.npc}_{uuid.uuid4().hex[:8]}"

    print(f"Thread: {thread_id}")
    while True:
        line = input("You: ").strip()
        if line.lower() in {"exit", "quit"}:
            break
        payload = DialogueTurnRequest(
            thread_id=thread_id,
            npc_id=args.npc,
            player_line=line,
            player_name=args.player,
            location=args.location,
            active_quests=[],
            inventory_flags=[],
            npc_disposition=0.3,
            time_of_day="morning",
        )
        response = dialogue_turn(payload)
        print(f"{args.npc} [{response.emotion}]: {response.line}")
        debug = response.debug
        effect_summary = ",".join(effect.type for effect in response.game_effects) or "none"
        print(
            f"Debug: intent={debug.intent} lore={debug.lore_chunks_used} "
            f"retries={debug.retry_count} effects={effect_summary}"
        )


if __name__ == "__main__":
    main()
