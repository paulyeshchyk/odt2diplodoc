# diplodoc_converter/strategies/footnotes.py
import re
from .base import TransformationStrategy

class FixFootnotesStrategy(TransformationStrategy):
    """Преобразует сноски Pandoc в формат, понятный Diplodoc."""
    
    def transform(self, content: str) -> str:
        # Pandoc может генерировать [^1] и внизу [^1]: текст
        # Diplodoc поддерживает стандартные сноски Markdown, ничего менять не надо.
        # Но если нужно изменить стиль – добавьте логику.
        return content