import re
from diplodoc_converter.fromODT.md.strategies.content.MDContentStrategy import (
    MDContentStrategy,
)
from ....model.figure_constants import REFERENCE_PATTERN


class MDContentStrategyFigureReferencesReplacer1(MDContentStrategy):
    def transform(self, content: str) -> str:
        # заменяем (рис. 2) на [@fig:2]
        return re.sub(REFERENCE_PATTERN, r"[@fig:\1]", content, flags=re.IGNORECASE)
