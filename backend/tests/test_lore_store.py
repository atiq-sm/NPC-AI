from pathlib import Path

from app.lore_store import LoreStore
from scripts.index_lore import build_index


def test_retrieval_returns_aldric_ore_lore() -> None:
    store = LoreStore(Path(__file__).resolve().parents[1] / "app" / "lore" / "index.json")

    chunks = store.retrieve(
        npc_id="blacksmith_aldric",
        location="village_forge",
        query="Where can I find iron ore?",
    )

    assert chunks
    assert any("old mine north of town" in chunk.text for chunk in chunks)
    assert all(chunk.npc_id in (None, "blacksmith_aldric") for chunk in chunks)
    assert all(chunk.location in (None, "village_forge") for chunk in chunks)


def test_retrieval_excludes_mismatched_npc() -> None:
    store = LoreStore(Path(__file__).resolve().parents[1] / "app" / "lore" / "index.json")

    chunks = store.retrieve(
        npc_id="village_elder",
        location="village_forge",
        query="Where can I find iron ore?",
    )

    assert all(chunk.npc_id in (None, "village_elder") for chunk in chunks)


def test_index_generation_includes_all_lore_lines() -> None:
    lore_dir = Path(__file__).resolve().parents[1] / "app" / "lore"

    index = build_index(lore_dir)
    texts = {chunk["text"] for chunk in index}

    assert "He trusts practical folk and prefers concise answers." in texts
    assert "Rumors say miners avoid the old tunnels unless paid in advance." in texts
    assert all("source_path" in chunk for chunk in index)
