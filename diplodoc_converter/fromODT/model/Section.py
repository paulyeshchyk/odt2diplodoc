# diplodoc_converter/section_parser.py

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List


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
