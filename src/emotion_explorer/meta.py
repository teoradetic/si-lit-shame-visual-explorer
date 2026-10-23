"""meta.json: definitions and counts that the app shows on its method page.

Each build step owns one top-level section and overwrites only that one.
"""

import json
from typing import Any

from emotion_explorer.paths import META_JSON


def read_meta() -> dict[str, Any]:
    if not META_JSON.exists():
        return {}
    return json.loads(META_JSON.read_text(encoding="utf-8"))


def write_meta_section(section: str, values: dict[str, Any]) -> None:
    meta = read_meta()
    meta[section] = values
    META_JSON.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
