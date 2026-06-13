import argparse
from diplodoc_converter.fromODT.converter import convert_odt_to_diplodoc
from diplodoc_converter.fromODT.config import (
    CacheSettings,
    LuaOptions,
    ParserSettings,
    ConversionConfig,
    OdtCrossReferences,
)
from diplodoc_converter.fromODT.config import PandocOptions
from diplodoc_converter.intoODT.config import MdToOdtConfig


def _parse_lua_filters(value: str | None) -> list[str] | None:
    if not value:
        return None
    filters = [f.strip() for f in value.split(",") if f.strip()]
    return filters if filters else None


def main():
    parser = argparse.ArgumentParser(
        description="Diplodoc Converter: импорт ODT в MD или сборка ODT из MD"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Режим работы"
    )

    # Подкоманда для импорта ODT -> MD
    parser_import = subparsers.add_parser(
        "import", help="Конвертация ODT в структуру Diplodoc (MD)"
    )
    parser_import.add_argument("odt_path", help="Путь к ODT файлу")
    parser_import.add_argument("output_dir", help="Папка для результата")
    parser_import.add_argument(
        "--max-heading-level",
        type=int,
        default=6,
        help="Макс. уровень заголовка для разделения (1-6)",
    )
    parser_import.add_argument(
        "--temp-dir", default=".temp_convert", help="Папка для временных файлов"
    )
    parser_import.add_argument(
        "--keep-cache", action="store_true", help="Не удалять временные файлы"
    )
    parser_import.add_argument(
        "--reuse-cache",
        action="store_true",
        help="Использовать кэш при повторном запуске",
    )
    parser_import.add_argument("--pandoc-format", help="Полная строка формата Pandoc")
    parser_import.add_argument(
        "--lua-filter",
        action="append",
        default=None,
        metavar="FILTER",
        help="Lua-фильтры. Можно передавать через запятую",
    )
    parser_import.add_argument("--lua-dir", default=None, help=argparse.SUPPRESS)
    parser_import.add_argument(
        "--enable-crossref",
        action="store_true",
        help="Включить обработку перекрёстных ссылок",
    )
    parser_import.add_argument(
        "--crossref-metadata-file", help="Файл конфигурации для pandoc-crossref (YAML)"
    )

    # Подкоманда для сборки ODT из MD
    parser_build = subparsers.add_parser(
        "build", help="Сборка ODT из иерархии MD-файлов (по toc.yaml)"
    )
    parser_build.add_argument(
        "-i", "--input-dir", help="Корневая папка документации (где лежит toc.yaml)"
    )
    parser_build.add_argument("-o", "--output", help="Путь к выходному ODT-файлу")
    parser_build.add_argument(
        "--reference",
        default=None,
        help="ODT-файл с пользовательскими стилями (reference-doc)",
    )
    parser_build.add_argument(
        "--width-threshold",
        type=int,
        default=700,
        help="Ширина в пикселях для масштабирования на 100%% (по умолч. 700)",
    )
    parser_build.add_argument(
        "--max-heading",
        type=int,
        default=6,
        help="Макс. уровень заголовка в выходном ODT (1-6)",
    )
    parser_build.add_argument(
        "--caption-position",
        choices=["below", "inside"],
        default="inside",
        help="Расположение подписи к рисункам",
    )

    args = parser.parse_args()

    if args.command == "import":
        # Обработка lua-фильтров
        run_import(args)

    elif args.command == "build":
        run_export(args)
    else:
        parser.print_help()


def run_export(args):
    MdToOdtConfig.update(
        DEFAULT_INPUT_DIR=args.input_dir,
        DEFAULT_OUTPUT_FILE=args.output,
        REFERENCE_ODT=args.reference,
        WIDTH_THRESHOLD=args.width_threshold,
        MAX_HEADING_LEVEL=args.max_heading,
        CAPTION_POSITION=args.caption_position,
    )
    from diplodoc_converter.intoODT.cli import run

    run()


def run_import(args):
    lua_filters = []
    if args.lua_filter:
        for item in args.lua_filter:
            parsed = _parse_lua_filters(item)
            if parsed:
                lua_filters.extend(parsed)

    parser_settings = ParserSettings(
        max_heading_level_for_single_page=args.max_heading_level
    )
    lua_options = LuaOptions(lua_filter_path=lua_filters, lua_dir=args.lua_dir)

    if args.pandoc_format:
        pandoc_options = PandocOptions(raw_format=args.pandoc_format)
    else:
        pandoc_options = PandocOptions(
            format="markdown",
            raw_html=True,
            pipe_tables=True,
            backtick_code_blocks=True,
            lua_options=lua_options,
        )

    odtCross = OdtCrossReferences(
        enable_crossref=args.enable_crossref,
        crossref_metadata_file=args.crossref_metadata_file,
    )

    cache_settings = CacheSettings(
        temp_dir=args.temp_dir, keep_cache=args.keep_cache, reuse_cache=args.reuse_cache
    )

    config = ConversionConfig(
        odt_path=args.odt_path,
        output_dir=args.output_dir,
        cache_settings=cache_settings,
        parser_settings=parser_settings,
        pandoc_options=pandoc_options,
        odt_crossreferences_options=odtCross,
    )
    convert_odt_to_diplodoc(config)


if __name__ == "__main__":
    main()
