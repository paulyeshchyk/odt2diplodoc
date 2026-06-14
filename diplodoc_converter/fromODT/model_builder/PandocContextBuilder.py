from pathlib import Path
from diplodoc_converter.fromODT.utils import Conversion_File_Utils
from diplodoc_converter.fromODT.pandoc_utils.PandocContext import PandocContext
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext


class PandocContextBuilder:
    def build(self, ctx: ConversionContext) -> PandocContext:
        odt_temp_path = Conversion_File_Utils.odt_temp_path(ctx.config)
        odt_path_absolute = Path(odt_temp_path).absolute()
        temp_media = Conversion_File_Utils.odt_temp_media_path(ctx.config)
        temp_md = Conversion_File_Utils.md_temp_path(ctx.config)
        return PandocContext(
            odt_path=odt_path_absolute,
            temp_md_path=temp_md,
            temp_media_dir=temp_media,
        )
