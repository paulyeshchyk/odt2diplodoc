import re
from .base import MDStrategy

class RemoveAnchorLinksStrategy(MDStrategy):
    """Удаляет конструкции []{#anchor-...} из Markdown."""
    def transform(self, content: str) -> str:
        # Удаляем []{#anchor-123} (любые цифры)
        return re.sub(r'\[\]\{#anchor-\d+\}', '', content)