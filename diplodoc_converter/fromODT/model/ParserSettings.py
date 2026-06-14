from dataclasses import dataclass
from typing import Callable, Optional

from diplodoc_converter.fromODT.model.Section import Section


@dataclass
class ParserSettings:
    """
    Настройки парсинга заголовков.
    max_heading_level_for_single_page: максимальный уровень заголовка (1-6).
        Заголовки этого уровня и выше создают отдельные md-файлы.
        По умолчанию 6 – все заголовки (H1-H6) становятся отдельными страницами.
        Если установить 2, то только H1 и H2 будут разделены, а H3 и ниже останутся внутри.
    """

    max_heading_level_for_single_page: int = 6
    normalize_headings: bool = True
    inherit_index_from_nonindexed: bool = False
    indexing_callback: Optional[Callable[[Section], bool]] = None
    enable_section_indexing: bool = False  # Оставим индексы теми, что были в оригинале
