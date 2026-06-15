import re

from .MDContentStrategy import MDContentStrategy


class MDContentStrategyAnchorLinksRemover(MDContentStrategy):
    """Удаляет конструкции []{#anchor-...} из Markdown."""

    def transform(self, content: str) -> str:
        # Удаляем []{#anchor-123} (любые цифры)
        return re.sub(r"\[\]\{#anchor-\d+\}", "", content)
