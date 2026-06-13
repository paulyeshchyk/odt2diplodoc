from diplodoc_converter.fromODT import config
from diplodoc_converter.fromODT.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.diplodoc_writer import shift_headings
from diplodoc_converter.fromODT.pipeline.stages.stage import Stage
from diplodoc_converter.fromODT.section_parser import Section
from diplodoc_converter.fromODT.utils import ensure_dir
import yaml
from pathlib import Path


class YamlStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        self.build_section_tree(ctx)

    def build_section_tree(
        self,
        ctx: ConversionContext,
    ) -> None:
        # Корневые файлы
        root_title = ConverterSettings.ROOT_TITLE
        output_dir = Path(ctx.config.output_dir).absolute()

        root_index_content = self.render_index_md(root_title, "Section", "")
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
        section_type: str,
        body: str,
    ) -> str:
        frontmatter = f"""---\ntitle: {title}\nsectionType: {section_type}\npureTitle: {title}\n---"""
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
        ensure_dir(folder_path)

        section_type = "Section" if sec.level == 1 else "Chapter"
        # Вычисляем сдвиг: для заголовка секции уровня L, хотим сделать его уровня 1

        section_type = "Section" if sec.level == 1 else "Chapter"

        if config.ParserSettings.normalize_headings:
            shift = 1 - sec.level  # правильный сдвиг
            shifted_body = shift_headings(sec.body, shift, min_level=2)
        else:
            shifted_body = sec.body

        md_content = self.render_index_md(sec.title, section_type, shifted_body)
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
