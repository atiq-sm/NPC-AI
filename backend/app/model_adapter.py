from __future__ import annotations

import json
from typing import Any

import requests
from pydantic import BaseModel, ValidationError


class OllamaAdapter:
    def __init__(self, model: str = "qwen2.5:7b-instruct", base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 160) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception:
            return "I can share what I know: the old mine north of town once had iron ore."

    def generate_json(self, prompt: str, schema_hint: type[BaseModel], retries: int = 1) -> dict[str, Any]:
        attempts = retries + 1
        last_error: Exception | None = None
        for attempt in range(attempts):
            extra = "\nReturn strict JSON only." if attempt else ""
            raw = self.generate_text(f"{prompt}{extra}", temperature=0.0, max_tokens=220)
            try:
                parsed = json.loads(raw)
                validated = schema_hint.model_validate(parsed)
                return validated.model_dump()
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc

        try:
            return schema_hint.model_validate({}).model_dump()
        except ValidationError:
            fallback: dict[str, Any] = {}
            for field_name, field_info in schema_hint.model_fields.items():
                annotation = field_info.annotation
                if annotation is bool:
                    fallback[field_name] = False
                elif annotation in (dict, dict[str, Any]):
                    fallback[field_name] = {}
                else:
                    fallback[field_name] = "unknown"
            if "error" in schema_hint.model_fields:
                fallback["error"] = str(last_error) if last_error else "json_parse_failed"
            return schema_hint.model_validate(fallback).model_dump()
