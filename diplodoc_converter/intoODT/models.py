# ------------------------------------------------------------
# Модель данных
# ------------------------------------------------------------
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class DocNode:
    """Узел дерева документации (глава или подглава)."""

    heading: str
    level: int
    path: Path | None = None  # Путь к md-файлу текущей главы (может отсутствовать)
    rel_path: Path | None = None  # Относительный путь для якорей
    children: List["DocNode"] | None = None  # Список дочерних подглав

    def __post_init__(self):
        if self.children is None:
            self.children = []
