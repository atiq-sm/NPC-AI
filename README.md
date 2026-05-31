# NPC-AI

NPC conversations using LLMs with RAG and LangGraph.

## Backend prototype

A backend-first dialogue prototype now lives in `/tmp/workspace/atiq-sm/NPC-AI/backend` with:

- FastAPI endpoints:
  - `GET /health`
  - `POST /dialogue/turn`
  - `GET /dialogue/threads/{thread_id}/last`
- LangGraph flow for intent classification, lore retrieval, draft generation, validation, retry/fallback, and conservative game effects.
- Local Ollama adapter (`qwen2.5:7b-instruct` default).
- Aldric vertical-slice lore, profile, and fallback content.
- CLI harness for quick local turn-by-turn checks.

## Run locally

```bash
cd /tmp/workspace/atiq-sm/NPC-AI/backend
python -m pip install -e .[dev]
uvicorn app.main:app --reload
```

## CLI harness

```bash
cd /tmp/workspace/atiq-sm/NPC-AI/backend
python -m app.cli --npc blacksmith_aldric --location village_forge
```

## Tests

```bash
cd /tmp/workspace/atiq-sm/NPC-AI/backend
pytest -q
```
