# diplodoc_converter/cli.py

import argparse
from diplodoc_converter.converter import convert_odt_to_diplodoc
from diplodoc_converter.config import CacheSettings, LuaOptions, ParserSettings, ConversionConfig, OdtCrossReferences
from diplodoc_converter.config import PandocOptions


def _parse_lua_filters(value: str | None) -> list[str] | None:
    if not value:
        return None
    filters = [f.strip() for f in value.split(',') if f.strip()]
    return filters if filters else None


def main():
    parser = argparse.ArgumentParser(description="Конвертация ODT в Diplodoc")
    
    # Позиционные аргументы — удобнее для вызова из расширения
    parser.add_argument("odt_path", help="Путь к ODT файлу")
    parser.add_argument("output_dir", help="Папка для результата")
    
    parser.add_argument("--max-heading-level", type=int, default=6, help="Макс. уровень заголовка для разделения (1-6)")
    parser.add_argument("--temp-dir", default=".temp_convert", help="Папка для временных файлов")
    parser.add_argument("--keep-cache", action="store_true", help="Не удалять временные файлы")
    parser.add_argument("--reuse-cache", action="store_true", help="Использовать кэш при повторном запуске")
    parser.add_argument("--pandoc-format", help="Полная строка формата Pandoc")
    
    parser.add_argument("--lua-filter", action="append", default=None, metavar="FILTER", help="Lua-фильтры. Можно передавать через запятую")
    parser.add_argument("--lua-dir", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--filter", default=None)

    parser.add_argument("--enable-crossref", action="store_true", help="Включить обработку перекрёстных ссылок через pandoc-crossref")
    parser.add_argument("--crossref-metadata-file", help="Файл конфигурации для pandoc-crossref (YAML)")    

    args = parser.parse_args()

    # Обработка lua-фильтров
    lua_filters = []
    if args.lua_filter:
        for item in args.lua_filter:
            parsed = _parse_lua_filters(item)
            if parsed:
                lua_filters.extend(parsed)
    if args.filter:
        lua_filters.extend(args.filter)
        
    parser_settings = ParserSettings(max_heading_level_for_single_page=args.max_heading_level)

    lua_options = LuaOptions(lua_filter_path=lua_filters, lua_dir=args.lua_dir)

    if args.pandoc_format:
        pandoc_options = PandocOptions(raw_format=args.pandoc_format)
    else:
        pandoc_options = PandocOptions(
            format="markdown",
            raw_html=True,
            pipe_tables=True,
            backtick_code_blocks=True,
            lua_options=lua_options
        )

    odtCross = OdtCrossReferences(
        enable_crossref = args.enable_crossref,
        crossref_metadata_file = args.crossref_metadata_file
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
        pandoc_options=pandoc_options,
        odt_crossreferences_options=odtCross
    )
    convert_odt_to_diplodoc(config)

def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    
if __name__ == "__main__":
    main()