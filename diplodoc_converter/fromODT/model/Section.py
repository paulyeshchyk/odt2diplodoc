# diplodoc_converter/section_parser.py

from typing import List
from dataclasses import dataclass
from pathlib import Path

from enum import Enum


class SectionType(Enum):
    PART = "part"
    SECTION = "section"
    CHAPTER = "chapter"
    PAGE = "page"


@dataclass
class Section:
    title: str
    pureTitle: str
    level: int
    body: str
    section_type: SectionType
    children: List["Section"]
    slug: str = ""  # короткое имя папки
    sectionIndex: str | None = None
    full_slug: Path | None = None  # полный путь от корня
    relative_path: Path | None = None
    anchor: str | None = None
