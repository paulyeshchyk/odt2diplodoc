from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.utils import Conversion_File_Utils
from .base import Stage


import shutil


class ODTCloneStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Клонирование ODT ...")
        Conversion_File_Utils.make_temp_dir(ctx.config)
        odt_temp_path = Conversion_File_Utils.odt_temp_path(ctx.config)
        shutil.copyfile(ctx.config.odt_path, odt_temp_path)
