import argparse
from diplodoc_converter.fromODT.Config import ConfigBuilder
from diplodoc_converter.fromODT.ConverterMessages import ConverterMessages
from diplodoc_converter.fromODT.config import CacheSettings
from diplodoc_converter.fromODT.pipeline.stages.GlobalStrategiesStage import (
    GlobalStrategiesStage,
)
from diplodoc_converter.fromODT.pipeline.stages.MarkdownStage import MarkdownStage
from diplodoc_converter.fromODT.pipeline.stages.SectionStrategiesStage import (
    SectionStrategiesStage,
)
from diplodoc_converter.fromODT.pipeline.pipeline import Pipeline
from diplodoc_converter.fromODT.pipeline.stages.SectionsStage import SectionsStage
from diplodoc_converter.fromODT.pipeline.stages.WipeCacheStage import WipeCacheStage
from diplodoc_converter.fromODT.pipeline.stages.WipeOutputStage import WipeOutputStage
from diplodoc_converter.fromODT.pipeline.stages.CopyImagesToSectionStage import (
    CopyImagesToSectionStage,
)
from diplodoc_converter.fromODT.pipeline.stages.InternalLinkProcessorStage import (
    InternalLinkProcessorStage,
)
from diplodoc_converter.fromODT.pipeline.stages.ReplaceCrossLinksStage import (
    ReplaceCrossLinksStage,
)
from diplodoc_converter.fromODT.pipeline.stages.YamlStage import YamlStage
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


messages = ConverterMessages(lang="ru")


def run_import(args):

    config_builder = ConfigBuilder()
    ctx = config_builder.build_conversion_context(args, messages)
    if ctx.config.cache_settings is None:
        ctx.config.cache_settings = CacheSettings()

    pipeline = Pipeline(
        [
            WipeOutputStage(),
            MarkdownStage(),
            GlobalStrategiesStage(),
            SectionsStage(),
            InternalLinkProcessorStage(),
            CopyImagesToSectionStage(),
            ReplaceCrossLinksStage(),
            SectionStrategiesStage(),
            YamlStage(),
            WipeCacheStage(),
        ]
    )
    pipeline.run(ctx)


if __name__ == "__main__":
    main()
