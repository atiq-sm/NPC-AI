# NPC-AI

Backend-first NPC dialogue stack using FastAPI + LangGraph. It supports intent classification, lore retrieval (RAG),
response validation/repair, and conservative game-effect extraction with a local Ollama adapter.

## Backend prototype

The backend prototype lives in `backend/` and includes:

- FastAPI endpoints:
  - `GET /health`
  - `POST /dialogue/turn`
  - `GET /dialogue/threads/{thread_id}/last`
- LangGraph flow for intent classification, lore retrieval, prompt assembly, draft generation, validation/repair,
  fallback, and conservative game-effect extraction.
- SQLite checkpointing for thread state (when `langgraph-checkpoint-sqlite` is installed).
- Local Ollama adapter (`qwen2.5:7b-instruct` default).
- Aldric vertical-slice lore, profile, and fallback content.
- CLI harness for quick local turn-by-turn checks.

## Run locally

```bash
cd backend
python -m pip install -e .[dev]
uvicorn app.main:app --reload
```

## CLI harness

```bash
cd backend
python -m app.cli --npc blacksmith_aldric --location village_forge
```

## Tests

```bash
cd backend
pytest -q
```
