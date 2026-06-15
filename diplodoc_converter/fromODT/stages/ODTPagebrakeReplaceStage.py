from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.odt.preprocessors.OdtPreprocessor_PageBreak import (
    OdtPreprocessor_PageBreak,
)
from diplodoc_converter.fromODT.utils import Conversion_File_Utils

from .base import Stage


class ODTPagebrakeReplaceStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Обработка разрыва страниц ...")
        odt_temp_path = Conversion_File_Utils.odt_temp_path(ctx.config)

        pageBrakePreprocessor = OdtPreprocessor_PageBreak()
        pageBrakePreprocessor.process(odt_temp_path)
        return super().process(ctx)
