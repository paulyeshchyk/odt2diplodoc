from .MDSectionStrategyTwoColumnTableNoteReplacer import (
    MDSectionStrategyTwoColumnTableNoteReplacer,
    HorizontalRuleNoteStrategy,
)
from .MDSectionStrategyImagesInFiguresWrap import MDSectionStrategyImagesInFiguresWrap
from .MDSectionStrategyPandocAttributesRemove import (
    MDSectionStrategyPandocAttributesRemove,
)

section_strategies = [
    MDSectionStrategyPandocAttributesRemove(),
    HorizontalRuleNoteStrategy(),
    MDSectionStrategyTwoColumnTableNoteReplacer(),
    MDSectionStrategyImagesInFiguresWrap(),
]
