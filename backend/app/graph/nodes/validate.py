from __future__ import annotations

import re

FORBIDDEN_TOPICS = {"airplane", "internet", "smartphone", "openai", "prompt"}


def _sentence_count(line: str) -> int:
    return len([p for p in re.split(r"[.!?]+", line.strip()) if p])


def validate_response(state: dict) -> dict:
    draft_line = state.get("draft_line", "").strip()
    errors: list[str] = []

    if not draft_line:
        errors.append("empty_response")
    if _sentence_count(draft_line) > 3:
        errors.append("too_many_sentences")
    if any(term in draft_line.lower() for term in FORBIDDEN_TOPICS):
        errors.append("forbidden_topic")
    if "as an ai" in draft_line.lower() or "system prompt" in draft_line.lower():
        errors.append("prompt_leakage")
    if len(set(draft_line.split())) < 3 and draft_line:
        errors.append("repeated_text")

    status = "valid" if not errors else "retry"
    retry_count = state.get("retry_count", 0)
    if errors and retry_count >= 2:
        status = "fallback"

    return {
        "validation_errors": errors,
        "validation_status": status,
    }
