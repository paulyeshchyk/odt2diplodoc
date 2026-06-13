# diplodoc_converter/md_strategy/table_separators.py
from .MDContentStrategy import MDContentStrategy


class MDContentStrategyTableSeparatorsFixer(MDContentStrategy):
    """Исправляет разделители таблиц для совместимости с Diplodoc."""

    def transform(self, content: str) -> str:
        # Pandoc иногда создаёт таблицы с лишними пробелами в разделителях
        # Например, | --- | --- | -> |---| ---|
        # Diplodoc стандартный markdown, обычно всё ок. При необходимости добавьте замены.
        return content
