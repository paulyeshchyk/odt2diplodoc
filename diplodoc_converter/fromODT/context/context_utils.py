import json
from pathlib import Path
import shutil

from diplodoc_converter.fromODT.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.odt.process_crossref import OdtCrossrefProcessor


def get_temp_dir(ctx: ConversionContext) -> Path:
    cache = ctx.config.cache_settings
    return Path(cache.temp_dir).absolute()


def get_temp_md(ctx: ConversionContext) -> Path:
    temp_dir = get_temp_dir(ctx)
    return temp_dir / ConverterSettings.TEMP_MD_FILENAME


def get_working_path(ctx: ConversionContext) -> str:

    working_path = ctx.config.odt_path
    enable_crossref = getattr(ctx.config.pandoc_options, "enable_crossref", False)
    if not enable_crossref:
        return working_path

    print(ctx.messages.get("crossref_enabled"))

    temp_dir = get_temp_dir(ctx)
    temp_odt = temp_dir / ConverterSettings.TEMP_ODT_FILENAME
    temp_odt.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ctx.config.odt_path, temp_odt)

    crossrefProcessor = OdtCrossrefProcessor()
    fig_map = crossrefProcessor.process_odt_crossrefs(temp_odt)
    fig_map_path = temp_odt.with_suffix(ConverterSettings.FIG_MAP_EXT)
    with open(fig_map_path, "w", encoding="utf-8") as f:
        json.dump(fig_map, f)
    working_path = str(temp_odt)
    return working_path
