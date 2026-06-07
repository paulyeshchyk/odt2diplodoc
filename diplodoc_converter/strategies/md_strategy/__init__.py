from .remove_empty_anchors_strategy import RemoveEmptyAnchorsStrategy
from .table_links_strategy import FixTableLinksStrategy
from .table_separators_strategy import FixTableSeparatorsStrategy
from .footnote_strategy import FixFootnotesStrategy

__all__ = [
    "RemoveEmptyAnchorsStrategy",
    "FixTableLinksStrategy",
    "FixTableSeparatorsStrategy",
    "FixFootnotesStrategy",
]

global_strategies = [
    RemoveEmptyAnchorsStrategy(),
    # FixTableLinksStrategy(), # если нужно – раскомментируйте
]
