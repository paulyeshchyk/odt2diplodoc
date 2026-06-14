from diplodoc_converter.intoODT.postProcessing.MD.ProcessingContext import (
    ProcessingContext,
)
from diplodoc_converter.intoODT.postProcessing.MD.MDNotesProcessor import (
    MDNotesProcessor,
)


class NoteBlockReplacer:
    @staticmethod
    def process(ctx: ProcessingContext) -> None:
        ctx.content = MDNotesProcessor.replace_note_blocks(ctx.content)
