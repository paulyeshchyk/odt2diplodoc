from diplodoc_converter.fromODT.md.strategies.content.MDContentStrategyPageBreakReplacer import (
    MDContentStrategyPageBreakReplacer,
)
from diplodoc_converter.fromODT.md.strategies.content.MDContentStrategyFigureReferencesReplacer import (
    MDContentStrategyFigureReferencesReplacer,
)
from diplodoc_converter.fromODT.md.strategies.content.MDContentStrategyAnchorLinksRemover import (
    MDContentStrategyAnchorLinksRemover,
)
from diplodoc_converter.fromODT.md.strategies.content.MDContentStrategyFigureReferencesReplacer1 import (
    MDContentStrategyFigureReferencesReplacer1,
)
from diplodoc_converter.fromODT.md.strategies.content.MDContentStrategyStyleNotesRestorer import (
    MDContentStrategyStyleNotesRestorer,
)

from .MDContentStrategyEmptyAnchorsRemover import MDContentStrategyEmptyAnchorsRemover
from .MDContentStrategyTableLinksFixer import MDContentStrategyTableLinksFixer
from .MDContentStrategyTableSeparatorsFixer import MDContentStrategyTableSeparatorsFixer
from .MDContentStrategyFootnotesReplacer import MDContentStrategyFootnotesReplacer

__all__ = [
    "MDContentStrategyAnchorLinksRemover",
    "MDContentStrategyEmptyAnchorsRemover",
    "MDContentStrategyTableLinksFixer",
    "MDContentStrategyTableSeparatorsFixer",
    "MDContentStrategyFootnotesReplacer",
    "MDContentStrategyFigureReferencesReplacer",
    "MDContentStrategyStyleNotesRestorer",
    "MDContentStrategyPageBreakReplacer",
]

global_strategies = [
    MDContentStrategyEmptyAnchorsRemover(),
    MDContentStrategyFigureReferencesReplacer1(),
    MDContentStrategyFigureReferencesReplacer(),
    MDContentStrategyAnchorLinksRemover(),
    MDContentStrategyStyleNotesRestorer(),
    MDContentStrategyPageBreakReplacer(),
    # FixTableLinksStrategy()
]
