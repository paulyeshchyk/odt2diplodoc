import argparse


class cli_args_builder:
    @staticmethod
    def build_args(parser):
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
        parser_import.add_argument(
            "--pandoc-format", help="Полная строка формата Pandoc"
        )
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
            "--crossref-metadata-file",
            help="Файл конфигурации для pandoc-crossref (YAML)",
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
        return args
