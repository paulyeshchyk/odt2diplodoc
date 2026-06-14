from dataclasses import dataclass


@dataclass
class ConverterSettings:
    """Константы, используемые в конвертере."""

    MEDIA_DIR = "media"
    TEMP_MD_FILENAME = "full_doc.md"
    TEMP_ODT_FILENAME = "crossref_input.odt"
    FIG_MAP_EXT = ".figmap.json"
    ROOT_TITLE = "Документация"
