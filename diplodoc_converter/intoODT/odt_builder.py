# ------------------------------------------------------------
# Сборщик ODT
# ------------------------------------------------------------
from diplodoc_converter.intoODT.odt_postprocessor import CrossReferenceStrategy, FigureCaptionStrategy, OdtPostProcessor
from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.markdown_processor import MarkdownProcessor
from diplodoc_converter.intoODT.utils import transliterate
from diplodoc_converter.intoODT.models import DocNode


import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List


class OdtBuilder:
    """Копирует ресурсы, собирает единый Markdown на основе дерева DocNode и запускает pandoc."""

    def __init__(self, root_dir: Path, nodes: List[DocNode]):
        self.root_dir = root_dir
        self.nodes = nodes
        self.anchor_map = {}

    @staticmethod
    def generate_anchor(rel_path: Path) -> str:
        """Генерирует уникальный латинский якорь из относительного пути файла."""
        parts = rel_path.with_suffix('').parts
        anchor = '_'.join(parts)
        # Принудительно транслитерируем и очищаем от спецсимволов
        anchor = transliterate(anchor)
        anchor = re.sub(r'[^a-zA-Z0-9_.-]', '_', anchor)
        return f"doc_{anchor}"

    def _build_anchor_map(self, nodes: List[DocNode]):
        for node in nodes:
            if node.rel_path:
                # Гарантируем сохранение нормализованного пути
                self.anchor_map[node.rel_path] = self.generate_anchor(node.rel_path)
            if node.children:
                self._build_anchor_map(node.children)

    def _copy_images_for_nodes(self, nodes: List[DocNode], temp_path: Path, copied_folders=None):
        """Рекурсивный обход дерева для копирования картинок из папок, где лежат md."""
        if copied_folders is None:
            copied_folders = set()

        for node in nodes:
            if node.path:
                src_folder = node.path.parent
                if src_folder not in copied_folders:
                    for item in src_folder.rglob("*"):
                        if item.is_file() and item.suffix.lower() in MdToOdtConfig.IMAGE_EXTENSIONS:
                            try:
                                rel_path = item.relative_to(self.root_dir)
                                rel_path = MdToOdtConfig.normalize_rel_path(rel_path)
                            except ValueError:
                                continue
                            dest_file = temp_path / rel_path
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dest_file)
                    copied_folders.add(src_folder)
            if node.children:
                self._copy_images_for_nodes(node.children, temp_path, copied_folders)

    def _write_node(self, node: DocNode, out_file, processor: MarkdownProcessor):
        """
        Рекурсивный обход по принципу:
        1. Название текущей главы
        2. Содержимое текущей главы (если есть)
        3. Подглавы в цикле (рекурсивный спуск)
        """
        # Определяем уровень заголовка (ограничиваем MAX_HEADING_LEVEL)
        level = min(node.level, MdToOdtConfig.MAX_HEADING_LEVEL)
        heading_mark = '#' * level

        # 1. Вставляем название главы
        if node.rel_path and node.rel_path in self.anchor_map:
            anchor = self.anchor_map[node.rel_path]
            out_file.write(f"{heading_mark} {node.heading} {{#{anchor} .unnumbered}}\n\n")
        else:
            out_file.write(f"{heading_mark} {node.heading}\n\n")

        # 2. Читаем и вставляем содержимое текущей главы
        if node.path and node.path.is_file():
            with open(node.path, 'r', encoding='utf-8') as inf:
                content = inf.read()

            if not content.strip():
                out_file.write("\n")  # Если файл пустой, просто перенос строки
            else:
                # Обрабатываем контент через процессор
                processed_content = processor.process(content, node)
                out_file.write(processed_content)
                # Жестко отделяем контент от последующих заголовков подглав
                out_file.write("\n\n")
        else:
            # Если это папка-контейнер без index.md
            out_file.write("\n")

        # 3. Передаем эстафету подглавам (если они есть)
        if node.children:
            for child in node.children:
                self._write_node(child, out_file, processor)

    def build(self, output_path: Path) -> None:
        if not self.nodes:
            print("[OdtBuild]: Нет элементов для сборки.")
            return

        # Строим карту якорей по всему дереву
        self._build_anchor_map(self.nodes)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            print("[OdtBuild]: Начат")

            # 1. Копируем картинки
            self._copy_images_for_nodes(self.nodes, temp_path)

            # 2. Сборка combined.md
            combined_md = temp_path / "combined.md"
            with open(combined_md, 'w', encoding='utf-8') as out:
                # Инициализируем процессор контента один раз
                processor = MarkdownProcessor(self.root_dir, temp_path, self.anchor_map)

                # Запускаем рекурсивную запись. 
                # Каждый node сам запишет свой заголовок, свой контент и вызовет своих детей.
                for node in self.nodes:
                    self._write_node(node, out, processor)

            print("[OdtBuild]: Закончен")

            # 3. Вызов pandoc
            self._run_pandoc(combined_md, output_path, temp_path)

            # 4. Постобработка ODT
            strategies = []
            strategies.append(FigureCaptionStrategy())
            strategies.append(CrossReferenceStrategy())
            postproc = OdtPostProcessor(output_path)
            postproc.run(strategies)

    def _run_pandoc(self, combined_md: Path, output_path: Path, cwd: Path) -> None:
            cmd = [
                "pandoc",
                str(combined_md),
                "-o", str(output_path.absolute()),
                "--resource-path", str(cwd),
                "--standalone"
            ]

            # Добавляем ссылку на ODT-шаблон, если файл существует
            if MdToOdtConfig.REFERENCE_ODT and Path(MdToOdtConfig.REFERENCE_ODT).is_file():
                cmd.extend(["--reference-doc", str(Path(MdToOdtConfig.REFERENCE_ODT).resolve())])

            try:
                # print("DEBUG: pandoc command:", " ".join(cmd))
                print(f"[Pandoc]: Начат. Команда {cmd}")


                current_env = os.environ.copy()
                current_env["PYTHONUTF8"] = "1"

                subprocess.run(cmd, check=True, cwd=cwd)
                print(f"[Pandoc]: Закончен. Файл: {output_path}")
            except subprocess.CalledProcessError as e:
                print(f"Ошибка pandoc: {e}")
            except FileNotFoundError:
                print("Pandoc не установлен")