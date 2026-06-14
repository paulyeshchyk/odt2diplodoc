from dataclasses import dataclass


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
