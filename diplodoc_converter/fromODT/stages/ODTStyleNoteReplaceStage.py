from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.os_file_utils import Os_File_Utils
from .Stage import Stage
from diplodoc_converter.fromODT.odt.preprocessors.OdtPreprocessor_StyleNote import (
    OdtPreprocessor_StyleNote,
)


class ODTStyleNoteReplaceStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        odt_temp_path = Os_File_Utils.odt_temp_path(ctx.config)

        notePreprocessor = OdtPreprocessor_StyleNote()
        notePreprocessor.process(odt_temp_path)
