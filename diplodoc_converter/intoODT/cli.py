#!/usr/bin/env python3
# diplodoc_converter/md_to_odt.py
"""
Сборка ODT из иерархии md-файлов по toc.yaml.
"""

import sys
from pathlib import Path

from diplodoc_converter.intoODT.odt_builder import OdtBuilder
from diplodoc_converter.intoODT.toc_parser import TocParser
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
