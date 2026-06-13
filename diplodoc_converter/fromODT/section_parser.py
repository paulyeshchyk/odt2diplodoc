# diplodoc_converter/section_parser.py

from typing import List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Section:
    title: str
    level: int
    body: str
    children: List["Section"]
    slug: str = ""  # короткое имя папки
    full_slug: Path | None = None  # полный путь от корня
    relative_path: Path | None = None
    anchor: str | None = None
