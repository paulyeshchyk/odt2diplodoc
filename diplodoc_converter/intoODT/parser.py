# ------------------------------------------------------------
# Парсер оглавлений
# ------------------------------------------------------------
from diplodoc_converter.intoODT.utils import extract_title_from_md
from diplodoc_converter.intoODT.models import DocNode


import yaml


from pathlib import Path
from typing import Any, Dict, List


class TocParser:
    """Загружает и обходит структуру toc.yaml, возвращает список FileInfo."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()   # абсолютный путь к корню документации

    def load_toc(self, toc_path: Path) -> List[Dict[str, Any]]:
        """Безопасно загружает toc.yaml, возвращает список элементов или [] при ошибке."""
        try:
            with open(toc_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"Не удалось прочитать {toc_path}: {e}")
            return []

        # print(f"load toc: {toc_path}")

        if isinstance(data, dict):
            items = data.get('items') or data.get('content')
            if items is None:
                # print(f"В {toc_path} нет ключа 'items' или 'content', пропускаем")
                return []
            if not isinstance(items, list):
                print(f"Поле items в {toc_path} не является списком, пропускаем")
                return []
            return items
        elif isinstance(data, list):
            return data
        else:
            print(f"Файл {toc_path} имеет неожиданный формат: {type(data)}, пропускаем")
            return []

    def collect_md_files(self, toc_dir: Path, toc_items: List[Dict[str, Any]], level: int = 1) -> List[DocNode]:
        nodes = []
        for item in toc_items:
            heading = item.get('name')
            href = item.get('href') or item.get('path')
            include = item.get('include')

            md_path = None
            rel_path = None
            sub_items = []
            sub_dir = toc_dir

            # 1. Include – вложенное оглавление (переходим в другую папку)
            if include and isinstance(include, dict):
                sub_toc_rel = include.get('path')
                if sub_toc_rel:
                    sub_toc_abs = (toc_dir / sub_toc_rel).resolve()
                    if sub_toc_abs.is_file():
                        sub_items = self.load_toc(sub_toc_abs)
                        sub_dir = sub_toc_abs.parent

                        # У include-файла может быть свой заглавный md (например, intro.md рядом)
                        # В Diplodoc обычно если есть include, то контентом является index.md в той папке
                        candidate_md = sub_dir / "index.md"
                        if candidate_md.is_file():
                            md_path = candidate_md

            # 2. Прямая ссылка на md-файл (например: "href: introduction.md")
            elif href and href.endswith('.md'):
                md_path = (toc_dir / href).resolve()

            # 3. Ссылка на YAML-файл конфигурации страницы
            elif href and href.endswith('.yaml'):
                yaml_path = (toc_dir / href).resolve()
                if yaml_path.is_file():
                    md_path = yaml_path.with_suffix('.md')

            # 4. Ссылка на папку (например: "href: getting-started")
            elif href:
                candidate_dir = (toc_dir / href).resolve()
                if candidate_dir.is_dir():
                    sub_dir = candidate_dir
                    sub_toc = candidate_dir / "toc.yaml"

                    # Если внутри папки есть свой toc.yaml — читаем его подглавы
                    if sub_toc.is_file():
                        sub_items = self.load_toc(sub_toc)

                    # Контентом САМОЙ этой папки является её index.md
                    candidate_md = candidate_dir / "index.md"
                    if candidate_md.is_file():
                        md_path = candidate_md

            # КРИТИЧЕСКИЙ БЛОК: Валидация и сбор метаданных
            if md_path and md_path.is_file():
                title_from_md = extract_title_from_md(md_path)
                heading = title_from_md or heading or md_path.stem
                rel_path = md_path.relative_to(self.root_dir)
            else:
                # Если файл не найден физически, но заголовок в toc.yaml объявлен,
                # мы всё равно создаем узел (виртуальную главу), чтобы не терять структуру подглав.
                md_path = None
                heading = heading or (Path(href).stem if href else "Без названия")

            # Создаем узел структуры
            node = DocNode(
                heading=heading,
                level=level,
                path=md_path,
                rel_path=rel_path
            )

            # Рекурсивно уходим вглубь, если нашли дочерние элементы
            if sub_items:
                node.children = self.collect_md_files(sub_dir, sub_items, level + 1)

            nodes.append(node)

        return nodes