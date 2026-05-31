from __future__ import annotations

import json
from pathlib import Path


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---\n"):
        return {}, raw
    _, rest = raw.split("---\n", 1)
    front, body = rest.split("---\n", 1)
    metadata = {}
    for line in front.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, body.strip()


def build_index(lore_dir: Path) -> list[dict]:
    chunks: list[dict] = []
    for path in sorted(lore_dir.glob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        for sentence in [line.strip() for line in body.splitlines() if line.strip()]:
            chunks.append(
                {
                    "text": sentence,
                    "npc_id": metadata.get("npc_id"),
                    "location": metadata.get("location"),
                    "quest_id": metadata.get("quest_id"),
                    "spoiler_level": int(metadata.get("spoiler_level", "0")),
                    "source_path": str(path.relative_to(lore_dir.parents[1])),
                }
            )
    return chunks


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    lore_dir = base_dir / "app" / "lore"
    index_path = lore_dir / "index.json"
    chunks = build_index(lore_dir)
    index_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    print(f"Indexed {len(chunks)} lore chunks to {index_path}")


if __name__ == "__main__":
    main()
