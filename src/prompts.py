"""Versioned prompt loading."""
from __future__ import annotations

import json

from src.config import settings


def load_prompt(name: str) -> str:
    registry_path = settings.paths.prompts_dir / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    version = registry["active"][name]
    prompt_file = registry["versions"][name][version]["file"]
    return (settings.paths.prompts_dir / prompt_file).read_text(encoding="utf-8")
