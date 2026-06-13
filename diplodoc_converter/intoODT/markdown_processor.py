# markdown_processor.py

# ------------------------------------------------------------
# Обработчик содержимого Markdown
# ------------------------------------------------------------
from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.utils import transliterate
from diplodoc_converter.intoODT.models import DocNode

from PIL import Image

import re
import urllib.parse
from pathlib import Path
from typing import Dict


class MarkdownProcessor:
    """Преобразует содержимое отдельного md-файла."""

    def __init__(self, root_dir: Path, temp_dir: Path, anchor_map: Dict[Path, str]):
        self.root_dir = root_dir
        self.temp_dir = temp_dir
        self.anchor_map = anchor_map
        self.used_anchors = set()

    @staticmethod
    def normalize_bullet_lists(content: str) -> str:
        """
        Заменяет маркеры списков '+' на стандартные '-',
        а также обеспечивает пустую строку перед списком, чтобы предотвратить слипание.
        """
        # Шаг 1: Заменяем '+' на '-' только в начале строк (учитывая пробелы перед ними)
        # re.MULTILINE обязателен
        content = re.sub(r"^(\s*)\+\s+", r"\1- ", content, flags=re.MULTILINE)

        # Шаг 2: Исправляем слипание с предыдущим текстом.
        # Ищем ситуацию, когда идет строка с текстом (не заголовок и не пустая),
        # а на следующей строке сразу начинается список '- '.
        # Добавляем между ними правильный перенос строки.
        def list_spacing_replacer(match):
            prev_line = match.group(1)
            list_line = match.group(2)
            # Если предыдущая строка уже пустая или это заголовок/блок кода, не трогаем
            if not prev_line.strip() or prev_line.strip().startswith(
                ("#", "-", "*", "+", "`")
            ):
                return match.group(0)
            return f"{prev_line}\n\n{list_line}"

        # Ищем пару строк: любая строка -> перенос строки -> строка списка
        pattern = r"^([^\n]+)\n(\s*-\s+.*)$"
        return re.sub(pattern, list_spacing_replacer, content, flags=re.MULTILINE)

    @staticmethod
    def remove_frontmatter(content: str) -> str:
        """Удаляет YAML-блок в начале файла (между --- и ---)."""
        lines = content.splitlines()
        if lines and lines[0].strip() == "---":
            end_idx = 1
            while end_idx < len(lines) and lines[end_idx].strip() != "---":
                end_idx += 1
            if end_idx < len(lines):
                return "\n".join(lines[end_idx + 1 :])
            else:
                return "\n".join(lines[1:])
        return content

    @staticmethod
    def remove_empty_headings(
        content: str,
        file_path: Path,
    ) -> str:
        """Удаляет строки, содержащие только # и пробелы (пустые заголовки)."""
        lines = content.splitlines()
        cleaned = []
        changed = False
        for line in lines:
            if re.match(r"^\\#", line):  # экранированный #
                cleaned.append(line)
                continue
            if re.match(r"^#{1,6}\s*$", line):
                # print(f"Пустой заголовок в {file_path}: '{line}' - удалён")
                changed = True
                continue
            cleaned.append(line)
        return "\n".join(cleaned) if changed else content

    def replace_note_blocks(self, content: str) -> str:
        """Заменяет {% note ... %} на fenced div с custom-style."""

        def replacer(match):
            note_type = match.group(1).lower()
            title = match.group(2)  # может быть None
            inner = match.group(3).strip()

            style_map = {
                "tip": "NoteTip",
                "warning": "NoteWarning",
                "alert": "NoteAlert",
                "info": "NoteInfo",
            }
            style = style_map.get(note_type, "Note")

            # Если есть заголовок, добавим его жирным в начало содержимого
            if title:
                inner = f"**{title}**\n\n{inner}"

            return f'::: {{custom-style="{style}"}}\n{inner}\n:::'

        pattern = r'\{% note (\w+)(?:\s+"([^"]+)")?\s*%\}(.*?)\{% endnote %\}'
        return re.sub(pattern, replacer, content, flags=re.DOTALL)

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
        clean = transliterate(text.lower()).replace(" ", "-")
        return re.sub(r"[^a-zA-Z0-9_.-]", "_", clean)

    def _resolve_single_link(
        self,
        text: str,
        raw_link: str,
        current_node: DocNode,
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
        full_link = self._clean_markdown_link(raw_link)
        path_part, anchor_part = (
            full_link.split("#", 1) if "#" in full_link else (full_link, "")
        )
        path_part_clean = path_part.lstrip("/")

        # 2. Быстрый выход: ссылка на инлайн-якорь внутри этой же статьи
        if not path_part_clean and anchor_part:
            return f"[{text}](#{self._normalize_anchor_text(anchor_part)})"

        # 3. Быстрый выход: ссылки на статические медиа-файлы
        if any(
            path_part_clean.lower().endswith(ext)
            for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".zip"]
        ):
            return f"[{text}]({raw_link})"

        # 4. Разрешение путей (Файловая система)
        abs_root = self.root_dir.resolve()
        current_node_parent_dir = self.getDocNode_parent_dir(current_node)

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
            final_anchor = f"{anchor_id}_{self._normalize_anchor_text(anchor_part)}"
        else:
            final_anchor = anchor_id

        return f"[{text}](#{final_anchor})"

    def getDocNode_parent_dir(self, current_node):
        current_node_path_parent = self.getDocNode_parent(current_node)
        return current_node_path_parent.resolve()

    def getDocNode_parent(self, current_node):
        current_node_path = current_node.path
        return current_node_path.parent

    def convert_internal_links(
        self,
        content: str,
        current_node: DocNode,
    ) -> str:
        """Точка входа для парсинга внутренних ссылок."""
        if not current_node.path:
            return content

        def replacer(match):
            whole_match = match.group(0)
            # Если регулярка поймала картинку `![alt](src)`, возвращаем её нетронутой
            if whole_match.startswith("!"):
                return whole_match

            text = match.group(1).strip()
            raw_link = match.group(2).strip()

            return self._resolve_single_link(text, raw_link, current_node)

        # Ловим обычные ссылки и ссылки-картинки одним махом
        pattern = r"!?\[([\s\S]*?)\]\(([\s\S]*?)\)"
        return re.sub(pattern, replacer, content)

    def process_images(
        self,
        content: str,
        current_node: DocNode,
    ) -> str:
        if not current_node.path:
            return content

        def replace_path(match):
            alt_text = match.group(1).strip()
            img_src = match.group(2).strip()
            figure_html = match.group(4) if match.group(4) else ""

            extracted_caption = ""
            if figure_html:
                caption_match = re.search(
                    r"<figcaption[^>]*>(.*?)</figcaption>", figure_html, re.DOTALL
                )
                if caption_match:
                    raw_caption = caption_match.group(1)
                    cleaned = re.sub(r"<[^>]+>", "", raw_caption).strip()
                    extracted_caption = re.sub(
                        r"^(Рисунок|Рис)\s*\d+\.\s*", "", cleaned, flags=re.IGNORECASE
                    ).strip()

            # Нормализация путей
            img_src = re.sub(r"/+", "/", img_src)
            img_src = re.sub(r"^\./", "", img_src)

            parent = self.getDocNode_parent_dir(current_node)
            abs_img = (parent / img_src).resolve()
            try:
                rel_img = abs_img.relative_to(self.root_dir)
            except ValueError:
                return match.group(0)

            rel_img = MdToOdtConfig.normalize_rel_path(rel_img)
            rel_img_str = "./" + rel_img.as_posix()
            rel_img_str = re.sub(r"/\./", "/", rel_img_str)
            rel_img_str = re.sub(r"/+", "/", rel_img_str)

            full_img_path = self.temp_dir / rel_img
            width = 0
            if full_img_path.exists():
                try:
                    with Image.open(full_img_path) as img:
                        width = img.width
                except Exception:
                    pass

            final_caption_text = extracted_caption if extracted_caption else alt_text

            # ЛОГИКА ДЛЯ РЕЖИМА INSIDE
            if MdToOdtConfig.CAPTION_POSITION == "inside":
                size_attr = (
                    "{{ width=100% }}" if width > MdToOdtConfig.WIDTH_THRESHOLD else ""
                )
                markdown_image = f"![]({rel_img_str}){size_attr}"
                if final_caption_text:
                    # Оставляем только чистые маркеры
                    markdown_image += (
                        f" %%%CAPTION_START%%%{final_caption_text}%%%CAPTION_END%%%"
                    )
                return markdown_image

            else:
                # Режим BELOW (стандартный текст снизу, без изменений)
                size_attr = (
                    "{ width=100% }" if width > MdToOdtConfig.WIDTH_THRESHOLD else ""
                )
                markdown_image = f"![{final_caption_text}]({rel_img_str}){size_attr}"
                return markdown_image

        pattern = (
            r"!\[([^\]]*)\]\(([^)]+)\)(\s*\{[^}]+\})?(?:\s*(<figure>.*?</figure>))?"
        )
        return re.sub(pattern, replace_path, content, flags=re.DOTALL)

    def shift_internal_headings(
        self,
        content: str,
        node_level: int,
        node_anchor: str,
    ) -> str:
        """Сдвигает уровни заголовков и генерирует для них УНИКАЛЬНЫЕ ЛАТИНСКИЕ ID."""

        shift = node_level + 1

        def replacer(match):
            hashes = match.group(1)
            title_text = match.group(2).strip()

            new_level = min(len(hashes) + shift, MdToOdtConfig.MAX_HEADING_LEVEL)

            # Транслитерируем текст подзаголовка для безопасного ID
            sub_anchor = transliterate(title_text.lower()).replace(" ", "-")
            sub_anchor = re.sub(r"[^a-zA-Z0-9_.-]", "_", sub_anchor)

            # Базовый составной ID
            full_heading_id = f"{node_anchor}_{sub_anchor}"

            # ЗАЩИТА ОТ ДУБЛИКАТОВ: Если такой ID уже был, добавляем числовой индекс
            if full_heading_id in self.used_anchors:
                counter = 1
                new_id = f"{full_heading_id}_{counter}"
                while new_id in self.used_anchors:
                    counter += 1
                    new_id = f"{full_heading_id}_{counter}"
                full_heading_id = new_id

            self.used_anchors.add(full_heading_id)

            return f"{'#' * new_level} {title_text} {{#{full_heading_id} .unnumbered}}"

        pattern = r"^(#{1,6})\s+(.+)$"
        return re.sub(pattern, replacer, content, flags=re.MULTILINE)

    def process(
        self,
        content: str,
        current_node: DocNode,
    ) -> str:
        content = self.remove_frontmatter(content)
        rp = current_node.rel_path
        if rp:
            node_anchor = self.anchor_map.get(rp, "doc")
            content = self.shift_internal_headings(
                content, current_node.level, node_anchor
            )
            content = self.normalize_bullet_lists(content)
            content = self.remove_empty_headings(
                content, current_node.path if current_node.path else Path("vnode")
            )
            content = self.replace_note_blocks(content)
            content = self.process_images(content, current_node)
            content = self.convert_internal_links(content, current_node)
        return content
