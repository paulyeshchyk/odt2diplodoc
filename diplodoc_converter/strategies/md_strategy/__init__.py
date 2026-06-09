from diplodoc_converter.strategies.md_strategy.fix_figure_references import FixFigureReferencesStrategy
from diplodoc_converter.strategies.md_strategy.replace_figure_refs import ReplaceFigureReferencesStrategy

from .remove_empty_anchors_strategy import RemoveEmptyAnchorsStrategy
from .table_links_strategy import FixTableLinksStrategy
from .table_separators_strategy import FixTableSeparatorsStrategy
from .footnote_strategy import FixFootnotesStrategy

__all__ = [
    "RemoveEmptyAnchorsStrategy",
    "FixTableLinksStrategy",
    "FixTableSeparatorsStrategy",
    "FixFootnotesStrategy",
    "FixFigureReferencesStrategy"
]

global_strategies = [
    RemoveEmptyAnchorsStrategy(),
    ReplaceFigureReferencesStrategy(),
    FixFigureReferencesStrategy()
    # FixTableLinksStrategy()
]
