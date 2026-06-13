# diplodoc_converter/md_strategy/base.py
from abc import ABC, abstractmethod


class MDContentStrategy(ABC):
    """Абстрактная стратегия преобразования Markdown."""

    @abstractmethod
    def transform(self, content: str) -> str:
        """Принимает строку Markdown, возвращает изменённую строку."""
        pass
