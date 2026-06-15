from pathlib import Path
from typing import Dict

from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.models import DocNode
from diplodoc_converter.intoODT.preprocessing.markdown_processor import (
    MarkdownProcessor,
)
from diplodoc_converter.intoODT.stages.OdtBuildContext import OdtBuildContext
from diplodoc_converter.intoODT.stages.OdtPipelineStep import OdtPipelineStep


class MarkdownCompilationStep(OdtPipelineStep):
    """Шаг 3: Генерация и компиляция единого Markdown файла (combined.md) из DocNode."""

    def execute(self, context: OdtBuildContext) -> None:
        context.combined_md_path = context.temp_dir / "combined.md"

        processor = MarkdownProcessor(
            context.root_dir, context.temp_dir, context.anchor_map
        )

        with open(context.combined_md_path, "w", encoding="utf-8") as out_file:
            for node in context.nodes:
                self._write_node(node, out_file, processor, context.anchor_map)

        print("[Pipeline]: Сборка combined.md завершена.")

    def _write_node(
        self,
        node: DocNode,
        out_file,
        processor: MarkdownProcessor,
        anchor_map: Dict[Path, str],
    ):
        level = min(node.level, MdToOdtConfig.MAX_HEADING_LEVEL)
        heading_mark = "#" * level

        # 1. Заголовок
        if node.rel_path and node.rel_path in anchor_map:
            anchor = anchor_map[node.rel_path]
            out_file.write(
                f"{heading_mark} {node.heading} {{#{anchor} .unnumbered}}\n\n"
            )
        else:
            out_file.write(f"{heading_mark} {node.heading}\n\n")

        # 2. Контент
        if node.path and node.path.is_file():
            with open(node.path, "r", encoding="utf-8") as inf:
                content = inf.read()

            if not content.strip():
                out_file.write("\n")
            else:
                processed_content = processor.process(content, node)
                out_file.write(processed_content)
                out_file.write("\n\n")
        else:
            out_file.write("\n")

        # 3. Рекурсивный спуск по подглавам
        if node.children:
            for child in node.children:
                self._write_node(child, out_file, processor, anchor_map)
