# diplodoc_converter/strategies/base.py
from abc import ABC, abstractmethod

class TransformationStrategy(ABC):
    """Абстрактная стратегия преобразования Markdown."""
    
    @abstractmethod
    def transform(self, content: str) -> str:
        """Принимает строку Markdown, возвращает изменённую строку."""
        pass