# markdown_processor.py

# ------------------------------------------------------------
# Обработчик содержимого Markdown
# ------------------------------------------------------------

from diplodoc_converter.intoODT.postProcessing.MD.BulletListNormalizer import (
    BulletListNormalizer,
)
from diplodoc_converter.intoODT.postProcessing.MD.EmptyHeadingRemover import (
    EmptyHeadingRemover,
)
from diplodoc_converter.intoODT.postProcessing.MD.FrontmatterRemover import (
    FrontmatterRemover,
)
from diplodoc_converter.intoODT.postProcessing.MD.HeadingShifter import HeadingShifter
from diplodoc_converter.intoODT.postProcessing.MD.ImageProcessor import ImageProcessor
from diplodoc_converter.intoODT.postProcessing.MD.InternalLinkConverter import (
    InternalLinkConverter,
)
from diplodoc_converter.intoODT.models import DocNode

from pathlib import Path
from typing import Callable, Dict, List

from diplodoc_converter.intoODT.postProcessing.MD.NoteBlockReplacer import (
    NoteBlockReplacer,
)
from diplodoc_converter.intoODT.postProcessing.MD.ProcessingContext import (
    ProcessingContext,
)


class MarkdownProcessor:
    """Преобразует содержимое отдельного md-файла."""

    def __init__(self, root_dir: Path, temp_dir: Path, anchor_map: Dict[Path, str]):
        self.root_dir = root_dir
        self.temp_dir = temp_dir
        self.anchor_map = anchor_map

    def process(self, content: str, current_node: DocNode) -> str:
        ctx = ProcessingContext(
            root_dir=self.root_dir,
            temp_dir=self.temp_dir,
            anchor_map=self.anchor_map,
            current_node=current_node,
            content=content,
        )
        processors: List[Callable[[ProcessingContext], None]] = [
            FrontmatterRemover.process,
            HeadingShifter().process,  # создаём экземпляр, чтобы иметь доступ к used_anchors
            BulletListNormalizer.process,
            EmptyHeadingRemover.process,
            NoteBlockReplacer.process,
            ImageProcessor.process,
            InternalLinkConverter(self.root_dir, self.anchor_map).process,
        ]
        for proc in processors:
            proc(ctx)
        return ctx.content
