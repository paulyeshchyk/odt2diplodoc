from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.odt.preprocessors.OdtPreprocessor_StyleNote import (
    OdtPreprocessor_StyleNote,
)
from diplodoc_converter.fromODT.utils import Conversion_File_Utils

from .base import Stage


class ODTStyleNoteReplaceStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Обработка стилей ...")
        odt_temp_path = Conversion_File_Utils.odt_temp_path(ctx.config)

        notePreprocessor = OdtPreprocessor_StyleNote()
        notePreprocessor.process(odt_temp_path)
