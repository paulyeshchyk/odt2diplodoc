from pathlib import Path
from diplodoc_converter.fromODT.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.context.context_utils import (
    get_temp_dir,
    get_temp_md,
    get_working_path,
)
from diplodoc_converter.fromODT.pandoc_wrapper import PandocContext
from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext


class PandocContextBuilder:
    def build(self, ctx: ConversionContext) -> PandocContext:
        temp_dir = get_temp_dir(ctx)
        working_path = get_working_path(ctx)
        temp_dir.mkdir(parents=True, exist_ok=True)
        odt_path_absolute = Path(working_path).absolute()
        temp_media = temp_dir / ConverterSettings.MEDIA_DIR
        temp_md = get_temp_md(ctx)
        return PandocContext(
            odt_path=odt_path_absolute,
            temp_md_path=temp_md,
            temp_media_dir=temp_media,
        )
