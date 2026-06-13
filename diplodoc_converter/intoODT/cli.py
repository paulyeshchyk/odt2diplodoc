#!/usr/bin/env python3
# diplodoc_converter/md_to_odt.py
"""
Сборка ODT из иерархии md-файлов по toc.yaml.
"""

import sys
from pathlib import Path

from diplodoc_converter.intoODT.odt_builder import OdtBuilder
from diplodoc_converter.intoODT.parser import TocParser
from diplodoc_converter.intoODT.config import MdToOdtConfig

# try:
# except ImportError:
#     print("Установите PyYAML: pip install pyyaml")
#     sys.exit(1)


# ------------------------------------------------------------
# Точка входа
# ------------------------------------------------------------
def run() -> None:
    """Запускает сборку ODT, используя текущие настройки MdToOdtConfig."""
    input_dir = Path(MdToOdtConfig.DEFAULT_INPUT_DIR)
    if not input_dir.is_dir():
        print(f"Директория {input_dir} не найдена")
        sys.exit(1)

    root_dir = input_dir.resolve()
    root_toc = root_dir / "toc.yaml"
    if not root_toc.is_file():
        print(f"Не найден {root_toc}")
        sys.exit(1)

    output_file = Path(MdToOdtConfig.DEFAULT_OUTPUT_FILE).resolve()

    try:
        parser = TocParser(root_dir)
        items = parser.load_toc(root_toc)
        if not items:
            print("Нет элементов для сборки (корневой toc.yaml пуст или повреждён).")
            sys.exit(1)

        file_infos = parser.collect_md_files(root_dir, items, level=1)
        builder = OdtBuilder(root_dir, file_infos)
        builder.build(output_file)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Сборка ODT из MD")
    parser.add_argument(
        "-i", "--input-dir", required=True, help="Корневая папка документации"
    )
    parser.add_argument("-o", "--output", required=True, help="Выходной ODT-файл")
    parser.add_argument(
        "--reference", default=None, help="ODT-файл с пользовательскими стилями"
    )
    parser.add_argument(
        "--width-threshold", type=int, default=700, help="Ширина для масштабирования"
    )
    parser.add_argument(
        "--max-heading", type=int, default=6, help="Макс. уровень заголовка"
    )
    parser.add_argument(
        "--caption-position",
        choices=["below", "inside"],
        default="inside",
        help="Расположение подписи: below – под картинкой, inside – внутри alt",
    )
    args = parser.parse_args()
    MdToOdtConfig.update(
        DEFAULT_INPUT_DIR=args.input_dir,
        DEFAULT_OUTPUT_FILE=args.output,
        REFERENCE_ODT=args.reference,
        WIDTH_THRESHOLD=args.width_threshold,
        MAX_HEADING_LEVEL=args.max_heading,
        CAPTION_POSITION=args.caption_position,
    )
    run()


if __name__ == "__main__":
    main()
