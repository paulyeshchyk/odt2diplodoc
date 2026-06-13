from pathlib import Path
from diplodoc_converter.fromODT.os_file_utils import Os_File_Utils
from diplodoc_converter.fromODT.pandoc_wrapper import PandocContext
from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext


class PandocContextBuilder:
    def build(self, ctx: ConversionContext) -> PandocContext:
        odt_temp_path = Os_File_Utils.odt_temp_path(ctx.config)
        odt_path_absolute = Path(odt_temp_path).absolute()
        temp_media = Os_File_Utils.odt_temp_media_path(ctx.config)
        temp_md = Os_File_Utils.md_temp_path(ctx.config)
        return PandocContext(
            odt_path=odt_path_absolute,
            temp_md_path=temp_md,
            temp_media_dir=temp_media,
        )
