import yaml


import re
from pathlib import Path


def extract_title_from_md(file_path: Path) -> str | None:
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    try:
        fm = yaml.safe_load(match.group(1))
        return fm.get("title")
    except yaml.YAMLError:
        return None
