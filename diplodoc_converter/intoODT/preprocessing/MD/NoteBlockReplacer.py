from diplodoc_converter.intoODT.preprocessing.MD.MDNotesProcessor import (
    MDNotesProcessor,
)
from diplodoc_converter.intoODT.preprocessing.MD.ProcessingContext import (
    ProcessingContext,
)


class NoteBlockReplacer:
    @staticmethod
    def process(ctx: ProcessingContext) -> None:
        ctx.content = MDNotesProcessor.replace_note_blocks(ctx.content)
