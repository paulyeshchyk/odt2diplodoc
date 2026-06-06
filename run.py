#!/usr/bin/env python3
# run.py
from diplodoc_converter.converter import convert_odt_to_diplodoc
from diplodoc_converter.config import CacheSettings, ParserSettings, ConversionConfig
from diplodoc_converter.config import PandocOptions

if __name__ == "__main__":
    # Простой вызов (все настройки по умолчанию)
    config = ConversionConfig(
        odt_path="manual.odt",
        output_dir="./gs10/docs/ru",
        cache_settings=CacheSettings(temp_dir="./gs10/.pandoc.cache", keep_cache=True, reuse_cache=True),
        parser_settings=ParserSettings(max_heading_level_for_single_page=6),
        pandoc_options= PandocOptions(
            format="markdown",
            raw_html=True,
            pipe_tables =  True,
            backtick_code_blocks = True
        )
    )
    convert_odt_to_diplodoc(config)
