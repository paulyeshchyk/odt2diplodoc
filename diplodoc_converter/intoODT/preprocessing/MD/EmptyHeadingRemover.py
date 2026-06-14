import re

from diplodoc_converter.intoODT.postProcessing.MD.ProcessingContext import (
    ProcessingContext,
)


from pathlib import Path


class EmptyHeadingRemover:
    @staticmethod
    def process(ctx: ProcessingContext) -> None:
        file_path = ctx.current_node.path if ctx.current_node.path else Path("vnode")
        ctx.content = EmptyHeadingRemover.remove_empty_headings(ctx.content, file_path)

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
