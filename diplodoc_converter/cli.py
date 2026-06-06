# diplodoc_converter/cli.py

import argparse
from diplodoc_converter.converter import convert_odt_to_diplodoc
from diplodoc_converter.config import CacheSettings, ParserSettings, ConversionConfig
from diplodoc_converter.config import PandocOptions

def main():
    parser = argparse.ArgumentParser(description="Конвертация ODT в Diplodoc")
    parser.add_argument("odt_path", help="Путь к ODT файлу")
    parser.add_argument("output_dir", help="Папка для результата")
    parser.add_argument("--max-heading-level", type=int, default=6, help="Макс. уровень заголовка для разделения (1-6)")
    parser.add_argument("--temp-dir", default=".temp_convert", help="Папка для временных файлов")
    parser.add_argument("--keep-cache", action="store_true", help="Не удалять временные файлы")
    parser.add_argument("--reuse-cache", action="store_true", help="Использовать кэш при повторном запуске")
    parser.add_argument("--pandoc-format", help="Полная строка формата Pandoc, например 'markdown+raw_html+pipe_tables'")
    parser.add_argument("--lua-filter", help="Путь к Lua-фильтру (например, no-img-size.lua)")
    
    args = parser.parse_args()

    parser_settings = ParserSettings(max_heading_level_for_single_page=args.max_heading_level)

    if args.pandoc_format:
        pandoc_options = PandocOptions(raw_format=args.pandoc_format)
    else:
        pandoc_options = PandocOptions(
            format="markdown",
            raw_html=True,
            pipe_tables=True,
            backtick_code_blocks=True,
            lua_filter_path=args.lua_filter
        )

    cache_settings = CacheSettings(
        temp_dir=args.temp_dir,
        keep_cache=args.keep_cache,
        reuse_cache=args.reuse_cache
    )

    config = ConversionConfig(
        odt_path=args.odt_path,
        output_dir=args.output_dir,
        cache_settings=cache_settings,
        parser_settings=parser_settings,
        pandoc_options=pandoc_options
    )
    convert_odt_to_diplodoc(config)

if __name__ == "__main__":
    main()