import re
from diplodoc_converter.strategies.md_strategy.base import MDStrategy
from ...figure_constants import REFERENCE_PATTERN

class ReplaceFigureReferencesStrategy(MDStrategy):
    def transform(self, content: str) -> str:
        # заменяем (рис. 2) на [@fig:2]
        return re.sub(REFERENCE_PATTERN, r'[@fig:\1]', content, flags=re.IGNORECASE)