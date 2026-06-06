# diplodoc_converter/strategies/table_links.py
import re
from .base import TransformationStrategy

class FixTableLinksStrategy(TransformationStrategy):
    """Исправляет ссылки в таблицах: убирает мусор из ячеек, превращает в нормальные Markdown-ссылки."""
    
    def transform(self, content: str) -> str:
        # Пример: внутри таблиц Pandoc часто генерирует [текст]{#anchor}
        # Удаляем {#anchor} внутри ячеек
        content = re.sub(r'(\[[^\]]*\])\{#anchor[^}]+\}', r'\1', content)
        # Другие правила можно добавить
        return content