from .two_column_table_note_strategy import TwoColumnTableNoteStrategy, HorizontalRuleNoteStrategy
from .figure_wrapper import WrapImagesInFiguresStrategy
from .remove_pandoc_attrs import RemovePandocAttributesStrategy

section_strategies = [
    RemovePandocAttributesStrategy(),
    HorizontalRuleNoteStrategy(),
    TwoColumnTableNoteStrategy(),
    WrapImagesInFiguresStrategy(),
]
