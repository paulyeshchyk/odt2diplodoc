# diplodoc_converter/strategies/table_separators.py
import re
from .base import TransformationStrategy

class FixTableSeparatorsStrategy(TransformationStrategy):
    """Исправляет разделители таблиц для совместимости с Diplodoc."""
    
    def transform(self, content: str) -> str:
        # Pandoc иногда создаёт таблицы с лишними пробелами в разделителях
        # Например, | --- | --- | -> |---| ---|
        # Diplodoc стандартный markdown, обычно всё ок. При необходимости добавьте замены.
        return content