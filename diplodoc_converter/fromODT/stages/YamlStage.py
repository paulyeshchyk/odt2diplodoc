import re

from diplodoc_converter.fromODT.model import ParserSettings
from diplodoc_converter.fromODT.model.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.utils.os_file_utils import Os_File_Utils
from .base import Stage
from diplodoc_converter.fromODT.model.Section import Section, SectionType
import yaml
from pathlib import Path


class YamlStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Обработка yaml ...")
        self.build_section_tree(ctx)

    def build_section_tree(
        self,
        ctx: ConversionContext,
    ) -> None:
        # Корневые файлы
        root_title = ConverterSettings.ROOT_TITLE
        output_dir = Path(ctx.config.output_dir).absolute()

        root_index_content = self.render_index_md(
            title=root_title,
            pureTitle=root_title,
            section_type=SectionType.PAGE,
            section_index="",
            body="",
        )
        (output_dir / "index.md").write_text(root_index_content, encoding="utf-8")

        root_index_yaml = {
            "title": root_title,
            "href": "index.md",
            "meta": {"title": root_title},
        }
        with open(output_dir / "index.yaml", "w", encoding="utf-8") as f:
            yaml.dump(root_index_yaml, f, allow_unicode=True, sort_keys=False, indent=2)

        if not ctx.sections:
            return

        # Рекурсивно создаём все секции
        for sec in ctx.sections:
            self._write_section(sec, output_dir)

        # Корневой toc.yaml
        root_items = []
        for sec in ctx.sections:
            root_items.append(
                {
                    "name": sec.title,
                    "href": f"{sec.slug}/index.md",
                    "include": {"path": f"{sec.slug}/toc.yaml", "mode": "link"},
                }
            )
        root_toc = {"title": root_title, "href": "index.yaml", "items": root_items}
        with open(output_dir / "toc.yaml", "w", encoding="utf-8") as f:
            yaml.dump(root_toc, f, allow_unicode=True, sort_keys=False, indent=2)

    def render_index_md(
        self,
        title: str,
        pureTitle: str,
        section_type: SectionType,
        section_index: str | None,
        body: str,
    ) -> str:
        translation_map = {
            SectionType.SECTION: "Section",
            SectionType.PART: "Part",
            SectionType.CHAPTER: "Chapter",
            SectionType.PAGE: "Page",
        }
        sectionTypeStr = translation_map.get(section_type or SectionType.PAGE)
        sectionIndexStr = ""
        if section_index:
            sectionIndexStr = str(section_index)
        frontmatter = f"""---\ntitle: {title}\npureTitle: {pureTitle}\nsectionType: {sectionTypeStr}\nsectionIndex: '{sectionIndexStr}'\n---"""
        return frontmatter + ("\n" + body if body.strip() else "")

    def _write_section(
        self,
        sec: Section,
        output_root: Path,
    ) -> None:
        """Создаёт файлы для одной секции по её full_slug. Рекурсивно вызывает для детей."""

        if sec.full_slug is None:
            raise RuntimeError(f"full_slug не установлен для секции '{sec.title}'")
        folder_path = output_root / sec.full_slug
        Os_File_Utils.ensure_dir(folder_path)

        # section_type = "Section" if sec.level == 1 else "Chapter"
        # Вычисляем сдвиг: для заголовка секции уровня L, хотим сделать его уровня 1

        # section_type = "Section" if sec.level == 1 else "Chapter"

        if ParserSettings.ParserSettings.normalize_headings:
            shift = 1 - sec.level  # правильный сдвиг
            shifted_body = SectionHeaderShifter.shift_headings(
                sec.body, shift, min_level=2
            )
        else:
            shifted_body = sec.body

        md_content = self.render_index_md(
            title=sec.title,
            pureTitle=sec.pureTitle,
            section_type=sec.section_type,
            section_index=sec.sectionIndex,
            body=shifted_body,
        )
        (folder_path / "index.md").write_text(md_content, encoding="utf-8")

        index_yaml = {
            "title": sec.title,
            "href": "index.md",
            "meta": {"title": sec.title},
        }
        with open(folder_path / "index.yaml", "w", encoding="utf-8") as f:
            yaml.dump(index_yaml, f, allow_unicode=True, sort_keys=False, indent=2)

        # Рекурсивно обрабатываем детей
        toc_items = []
        for child in sec.children:
            self._write_section(child, output_root)
            toc_items.append(
                {
                    "name": child.title,
                    "href": f"{child.slug}/index.md",
                    "include": {"path": f"{child.slug}/toc.yaml", "mode": "link"},
                }
            )

        toc_yaml = {"title": sec.title, "href": "index.yaml", "items": toc_items}
        with open(folder_path / "toc.yaml", "w", encoding="utf-8") as f:
            yaml.dump(toc_yaml, f, allow_unicode=True, sort_keys=False, indent=2)


class SectionHeaderShifter:
    @staticmethod
    def shift_headings(content: str, shift: int, min_level: int = 1) -> str:
        """Сдвигает уровни Markdown-заголовков на shift, не опуская ниже min_level."""

        def repl(m):
            hashes = m.group(1)
            new_level = len(hashes) + shift
            if new_level < min_level:
                new_level = min_level
            return "#" * new_level + m.group(2)

        pattern = r"^(#{1,6})(\s+.*)$"
        return re.sub(pattern, repl, content, flags=re.MULTILINE)
