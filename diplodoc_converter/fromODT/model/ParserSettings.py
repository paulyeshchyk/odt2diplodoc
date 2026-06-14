from dataclasses import dataclass


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
