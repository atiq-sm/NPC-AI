from __future__ import annotations

import re
from pathlib import Path

FORBIDDEN_TOPICS = {
    "airplane",
    "internet",
    "smartphone",
    "openai",
    "prompt",
    "system prompt",
    "as an ai",
    "video game",
    "game ui",
    "fourth wall",
}
PROFILE_TOPIC_TERMS = {
    "modern technology": {"airplane", "internet", "smartphone", "computer", "screen"},
    "fourth-wall references": {"player", "game", "quest id", "map marker", "dialogue system"},
}
KNOWN_CONTEXT_IDS = {"find_iron_ore", "iron_mines"}


def _sentence_count(line: str) -> int:
    return len([p for p in re.split(r"[.!?]+", line.strip()) if p])


def _load_profile_forbidden_topics(npc_id: str) -> set[str]:
    profile_path = Path(__file__).resolve().parents[2] / "profiles" / f"{npc_id}.yaml"
    if not profile_path.exists():
        return set()

    topics: set[str] = set()
    in_forbidden = False
    for raw_line in profile_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "forbidden_topics:":
            in_forbidden = True
            continue
        if in_forbidden and line.startswith("- "):
            topics.add(line[2:].strip())
            continue
        if in_forbidden and line and not line.startswith("- "):
            break
    return topics


def _has_repeated_text(line: str) -> bool:
    words = re.findall(r"[a-z0-9']+", line.lower())
    if len(words) < 4:
        return False
    if len(set(words)) <= max(2, len(words) // 3):
        return True
    pairs = list(zip(words, words[1:]))
    return len(pairs) != len(set(pairs))


def validate_response(state: dict) -> dict:
    draft_line = state.get("draft_line", "").strip()
    request = state["request"]
    lower_line = draft_line.lower()
    errors: list[str] = []

    if not draft_line:
        errors.append("empty_response")
    if _sentence_count(draft_line) > 3:
        errors.append("too_many_sentences")
    if any(term in lower_line for term in FORBIDDEN_TOPICS):
        errors.append("forbidden_topic")
    for topic in _load_profile_forbidden_topics(request["npc_id"]):
        if any(term in lower_line for term in PROFILE_TOPIC_TERMS.get(topic, {topic})):
            errors.append("profile_forbidden_topic")
            break
    if "as an ai" in lower_line or "system prompt" in lower_line:
        errors.append("prompt_leakage")
    if _has_repeated_text(draft_line):
        errors.append("repeated_text")
    allowed_ids = set(request.get("active_quests", [])) | KNOWN_CONTEXT_IDS
    ids_in_line = set(re.findall(r"\b[a-z]+(?:_[a-z0-9]+)+\b", lower_line))
    unknown_ids = ids_in_line - allowed_ids
    if unknown_ids:
        errors.append("unknown_game_context_id")

    status = "valid" if not errors else "retry"
    retry_count = state.get("retry_count", 0)
    if errors and retry_count >= 2:
        status = "fallback"

    return {
        "validation_errors": errors,
        "validation_status": status,
    }
