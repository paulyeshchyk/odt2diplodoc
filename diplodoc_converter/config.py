# diplodoc_converter/config.py

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CacheSettings:
    """
    Настройки временного кэша при конвертации.

    temp_dir:   папка для временных файлов (по умолчанию ".temp_convert")
    keep_cache: если True, временные файлы НЕ удаляются после завершения
    reuse_cache: если True и временные файлы уже существуют, Pandoc НЕ вызывается повторно
    """
    temp_dir: str = ".temp_convert"
    keep_cache: bool = False
    reuse_cache: bool = False

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


@dataclass
class PandocOptions:
    """
    Настройки формата вывода Pandoc.
    """
    format: str = "markdown"
    pipe_tables: Optional[bool] = None
    backtick_code_blocks: Optional[bool] = None
    link_attributes: Optional[bool] = None
    raw_html: Optional[bool] = None
    raw_format: Optional[str] = None
    
    # Изменено: теперь список строк
    lua_filter_path: Optional[List[str]] = field(default_factory=list)

    def to_pandoc_string(self) -> str:
        """Формирует строку вида "markdown+pipe_tables-raw_html"."""
        if self.raw_format is not None:
            return self.raw_format
        
        result = self.format
        for field_name, field_value in self.__dict__.items():
            if field_name in ("format", "lua_filter_path", "raw_format") or field_value is None:
                continue
            if field_value:
                result += f"+{field_name}"
            else:
                result += f"-{field_name}"
        return result

@dataclass
class ConversionConfig:
    """
    Полная конфигурация конвертации.
    """
    odt_path: str                    # путь к исходному ODT
    output_dir: str                  # куда сохранить результат
    cache_settings: CacheSettings   # настройки кэша (можно импортировать позже)
    parser_settings: ParserSettings # настройки парсинга (по умолчанию все заголовки)
    pandoc_options: PandocOptions