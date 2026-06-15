from diplodoc_converter.intoODT.preprocessing.MD.ProcessingContext import (
    ProcessingContext,
)


class FrontmatterRemover:
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
    def process(ctx: ProcessingContext) -> None:
        ctx.content = FrontmatterRemover.remove_frontmatter(ctx.content)
