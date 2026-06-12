# diplodoc_converter/md_strategy/table_separators.py
import re
from .base import MDStrategy

class FixTableSeparatorsStrategy(MDStrategy):
    """Исправляет разделители таблиц для совместимости с Diplodoc."""
    
    def transform(self, content: str) -> str:
        # Pandoc иногда создаёт таблицы с лишними пробелами в разделителях
        # Например, | --- | --- | -> |---| ---|
        # Diplodoc стандартный markdown, обычно всё ок. При необходимости добавьте замены.
        return content