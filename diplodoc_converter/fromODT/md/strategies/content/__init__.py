from .MDContentStrategyPageBreakReplacer import MDContentStrategyPageBreakReplacer
from .MDContentStrategyFigureReferencesReplacer import (
    MDContentStrategyFigureReferencesReplacer,
)
from .MDContentStrategyAnchorLinksRemover import MDContentStrategyAnchorLinksRemover
from .MDContentStrategyFigureReferencesReplacer1 import (
    MDContentStrategyFigureReferencesReplacer1,
)
from .MDContentStrategyStyleNotesRestorer import MDContentStrategyStyleNotesRestorer

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
