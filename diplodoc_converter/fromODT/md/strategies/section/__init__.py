from .MDSectionStrategyImagesInFiguresWrap import MDSectionStrategyImagesInFiguresWrap
from .MDSectionStrategyPandocAttributesRemove import (
    MDSectionStrategyPandocAttributesRemove,
)
from .MDSectionStrategyTwoColumnTableNoteReplacer import (
    # MDSectionStrategyTwoColumnTableNoteReplacer,
    HorizontalRuleNoteStrategy,
)

section_strategies = [
    MDSectionStrategyPandocAttributesRemove(),
    HorizontalRuleNoteStrategy(),
    # MDSectionStrategyTwoColumnTableNoteReplacer(),
    MDSectionStrategyImagesInFiguresWrap(),
]
