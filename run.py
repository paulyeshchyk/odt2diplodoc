#!/usr/bin/env python3
# run.py
from diplodoc_converter.converter import convert_odt_to_diplodoc
from diplodoc_converter.cache_settings import CacheSettings

if __name__ == "__main__":
    # Вариант 1: со стандартными настройками
    # convert_odt_to_diplodoc("manual.odt", "./docs/ru")
    
    # Вариант 2: с сохранением кэша и его повторным использованием
    settings = CacheSettings(
        temp_dir="./gs10/.pandoc.cache",   # своя папка для временных файлов
        keep_cache=True,            # не удалять после конвертации
        reuse_cache=True            # при следующем запуске использовать без Pandoc
    )
    convert_odt_to_diplodoc("manual.odt", "./gs10/docs/ru", cache_settings=settings)