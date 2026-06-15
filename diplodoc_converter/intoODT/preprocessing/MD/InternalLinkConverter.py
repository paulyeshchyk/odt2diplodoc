import re
import urllib.parse
from pathlib import Path
from typing import Dict

from diplodoc_converter.intoODT.models import DocNode
from diplodoc_converter.intoODT.preprocessing.MD.DocNodeUtils import DocNodeUtils
from diplodoc_converter.intoODT.preprocessing.MD.ProcessingContext import (
    ProcessingContext,
)
from diplodoc_converter.intoODT.Transliterator import Transliterator


class InternalLinkConverter:
    def __init__(self, root_dir: Path, anchor_map: Dict[Path, str]):
        self.root_dir = root_dir
        self.anchor_map = anchor_map

    def process(self, ctx: ProcessingContext) -> None:
        if not ctx.current_node.path:
            return
        ctx.content = self._convert_links(ctx.content, ctx.current_node)

    def _convert_links(self, content: str, current_node: DocNode) -> str:
        def replacer(match):
            whole_match = match.group(0)
            if whole_match.startswith("!"):
                return whole_match
            text = match.group(1).strip()
            raw_link = match.group(2).strip()
            return self._resolve_single_link(text, raw_link, current_node)

        pattern = r"!?\[([\s\S]*?)\]\(([\s\S]*?)\)"
        return re.sub(pattern, replacer, content)

    def _resolve_single_link(
        self, text: str, raw_link: str, current_node: DocNode
    ) -> str:
        """
        Бизнес-логика разбора одной ссылки.
        Возвращает либо измененную внутреннюю ссылку, либо исходную.
        """
        if raw_link.startswith(("http://", "https://", "mailto:", "ftp:")):
            return f"[{text}]({raw_link})"

        if raw_link.startswith("#fig-"):
            return f"[{text}]({raw_link})"

        # 1. Очистка и деление на файл и инлайн-якорь
        full_link = InternalLinkConverter._clean_markdown_link(raw_link)
        path_part, anchor_part = (
            full_link.split("#", 1) if "#" in full_link else (full_link, "")
        )
        path_part_clean = path_part.lstrip("/")

        # 2. Быстрый выход: ссылка на инлайн-якорь внутри этой же статьи
        if not path_part_clean and anchor_part:
            return f"[{text}](#{InternalLinkConverter._normalize_anchor_text(anchor_part)})"

        # 3. Быстрый выход: ссылки на статические медиа-файлы
        if any(
            path_part_clean.lower().endswith(ext)
            for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".zip"]
        ):
            return f"[{text}]({raw_link})"

        # 4. Разрешение путей (Файловая система)
        abs_root = self.root_dir.resolve()
        current_node_parent_dir = DocNodeUtils.getDocNode_parent_dir(current_node)

        try:
            target_abs = (current_node_parent_dir / path_part_clean).resolve()
        except Exception:
            return f"[{text}]({raw_link})"

        if target_abs.is_dir():
            target_abs = target_abs / "index.md"

        try:
            target_rel = target_abs.relative_to(abs_root)
        except ValueError:
            return f"[{text}]({raw_link})"

        # 5. Поиск соответствия в anchor_map
        target_key = target_rel.as_posix()
        anchor_id = None
        for key_path, val_id in self.anchor_map.items():
            if Path(key_path).as_posix() == target_key:
                anchor_id = val_id
                break

        if not anchor_id:
            # print(f"ERROR: Ссылка не найдена в anchor_map! Искали ключ: '{target_key}'")
            return f"[{text}]({raw_link})"

        # 6. Сборка финального латинского якоря
        if anchor_part:
            final_anchor = f"{anchor_id}_{InternalLinkConverter._normalize_anchor_text(anchor_part)}"
        else:
            final_anchor = anchor_id

        return f"[{text}](#{final_anchor})"

    @staticmethod
    def _clean_markdown_link(raw_link: str) -> str:
        """Декодирует URL и очищает строку ссылки от переносов и title."""
        # Склеиваем случайные переносы строк
        link = re.sub(r"\s+", "", raw_link)
        # Декодируем %D0%...
        link = urllib.parse.unquote(link)
        # Отрезаем "title", если он передан в конце (например: `(link.md "Title")`)
        return link.split()[0]

    @staticmethod
    def _normalize_anchor_text(text: str) -> str:
        """Транслитерирует и очищает текст подзаголовка для использования в ID."""
        clean = Transliterator.transliterate(text.lower()).replace(" ", "-")
        return re.sub(r"[^a-zA-Z0-9_.-]", "_", clean)
