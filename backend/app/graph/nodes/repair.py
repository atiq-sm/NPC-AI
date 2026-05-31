from __future__ import annotations


def repair_prompt(state: dict) -> dict:
    errors = ", ".join(state.get("validation_errors", []))
    prompt = (
        f"{state['prompt']}\n"
        f"Repair the response. Previous validation errors: {errors}. "
        "Return only one grounded NPC reply under 3 sentences."
    )
    return {"prompt": prompt, "retry_count": state.get("retry_count", 0) + 1}
