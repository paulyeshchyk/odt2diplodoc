from dataclasses import dataclass

from diplodoc_converter.fromODT.model.CacheSettings import CacheSettings
from diplodoc_converter.fromODT.model.OdtCrossReferences import OdtCrossReferences
from diplodoc_converter.fromODT.model.ParserSettings import ParserSettings
from diplodoc_converter.fromODT.pandoc_utils.PandocOptions import (
    PandocOptions,
)


@dataclass
class ConversionConfig:
    """
    Полная конфигурация конвертации.
    """

    odt_path: str  # путь к исходному ODT
    output_dir: str  # куда сохранить результат
    cache_settings: CacheSettings  # настройки кэша (можно импортировать позже)
    parser_settings: ParserSettings  # настройки парсинга (по умолчанию все заголовки)
    pandoc_options: PandocOptions
    odt_crossreferences_options: OdtCrossReferences
