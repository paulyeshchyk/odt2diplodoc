from .MDContentStrategyAnchorLinksRemover import MDContentStrategyAnchorLinksRemover
from .MDContentStrategyEmptyAnchorsRemover import MDContentStrategyEmptyAnchorsRemover
from .MDContentStrategyFigureReferencesReplacer import (
    MDContentStrategyFigureReferencesReplacer,
)
from .MDContentStrategyFigureReferencesReplacer1 import (
    MDContentStrategyFigureReferencesReplacer1,
)
from .MDContentStrategyFootnotesReplacer import MDContentStrategyFootnotesReplacer
from .MDContentStrategyPageBreakReplacer import MDContentStrategyPageBreakReplacer
from .MDContentStrategyStyleNotesRestorer import MDContentStrategyStyleNotesRestorer
from .MDContentStrategyTableLinksFixer import MDContentStrategyTableLinksFixer
from .MDContentStrategyTableSeparatorsFixer import MDContentStrategyTableSeparatorsFixer

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
