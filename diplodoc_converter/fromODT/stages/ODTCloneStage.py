from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.os_file_utils import Os_File_Utils
from .Stage import Stage


import shutil


class ODTCloneStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        Os_File_Utils.make_temp_dir(ctx.config)
        odt_temp_path = Os_File_Utils.odt_temp_path(ctx.config)
        shutil.copyfile(ctx.config.odt_path, odt_temp_path)
