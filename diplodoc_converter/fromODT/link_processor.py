# diplodoc_converter/link_processor.py

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from diplodoc_converter.fromODT.stages.MDSectionsStage import (
    SectionFlatten,
)
from diplodoc_converter.fromODT.utils.os_file_utils import Os_File_Utils

from .model.Section import Section


def normalize_title(title: str) -> str:
    s = re.sub(r"[^\w\s-]", "", title.lower())
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s


def build_slug_and_anchor_maps(
    sections: Optional[List[Section]],
    base_output_dir: Path,
) -> Tuple[Dict[str, Path], Dict[str, Path]]:
    """
    Присваивает секциям slug (имя папки) и full_slug (путь от корня).
    Возвращает (slug_map, anchor_map)
    """

    def assign_slugs(
        sec: Section,
        parent_full: Path = Path(),
    ):
        # Генерируем имя для текущей секции
        part = Os_File_Utils.generate_folder_name(sec.title)
        if not part:
            part = "bez_nazvaniya"
        # Уникализация в пределах одного родителя (если нужно, можно добавить счётчик)
        # Для простоты оставляем как есть, но можно использовать parent_full для контекста
        sec.slug = part
        sec.full_slug = parent_full / part
        for child in sec.children:
            assign_slugs(child, sec.full_slug)

    if sections:
        for sec in sections:
            assign_slugs(sec, Path())

    slug_map = {}
    anchor_map = {}
    for sec in SectionFlatten.flatten_sections(sections):
        if sec.full_slug is None:
            raise RuntimeError(f"full_slug не установлен для секции '{sec.title}'")
        rel_path = sec.full_slug / "index.md"
        norm = normalize_title(sec.title)
        slug_map[norm] = rel_path
        slug_map[sec.slug] = rel_path  # короткое имя тоже может быть полезно
        if sec.anchor:
            anchor_map[sec.anchor] = rel_path
    return slug_map, anchor_map


def replace_internal_links(
    text: str,
    slug_map: Dict[str, Path],
    anchor_map: Dict[str, Path],
    current_section_slug: str,
) -> str:
    """Заменяет внутренние ссылки на относительные пути от текущей секции."""
    import os

    def rel_path(target: Path, start: Path) -> str:
        # target и start – относительные пути от output_dir
        # Вычисляем относительный путь от start до target
        rel = os.path.relpath(target, start=start)
        return rel.replace("\\", "/")

    def repl(match):
        full_match = match.group(0)
        link_text = match.group(1)
        target = match.group(2)
        if target.endswith(".md"):
            target = target[:-3]
        if target.startswith("#"):
            target = target[1:]
            # Сначала пробуем как якорь
            if target in anchor_map:
                target_path = anchor_map[target]
                # current_section_slug – это full_slug текущей секции (строка)
                current_dir = Path(current_section_slug)
                rel = rel_path(target_path, start=current_dir)
                # print(f"Заменяем ссылку {full_match} -> на {rel}")
                return f"[{link_text}]({rel})"
            # Затем как нормализованный заголовок
            target_norm = normalize_title(target)
            if target_norm in slug_map:
                target_path = slug_map[target_norm]
                current_dir = Path(current_section_slug)
                rel = rel_path(target_path, start=current_dir)
                return f"[{link_text}]({rel})"
        return full_match

    pattern = r"\[([^\]]+)\]\((?!https?://|mailto:)([^)]+)\)"
    return re.sub(pattern, repl, text)
