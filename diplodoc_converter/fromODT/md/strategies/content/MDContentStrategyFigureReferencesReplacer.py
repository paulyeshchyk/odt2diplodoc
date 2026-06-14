# strategies/md_strategy/fix_figure_references.py
import re
from .MDContentStrategy import MDContentStrategy
from ....model.figure_constants import (
    PLACEHOLDER_PATTERN,
    FIGURE_MARKER,
    SOURCE_IMAGE_FOLDER,
    TARGET_IMAGE_FOLDER,
)


class MDContentStrategyFigureReferencesReplacer(MDContentStrategy):
    def transform(self, content: str) -> str:
        # 1. Находим номера рисунков из подписей {#fig:N}
        fig_numbers = re.findall(rf"{{#{FIGURE_MARKER}:(\d+)}}", content)
        # 2. Находим пустые ссылки (рис. )
        ref_placeholders = list(
            re.finditer(PLACEHOLDER_PATTERN, content, re.IGNORECASE)
        )
        # 3. Заменяем последовательно (с конца)
        new_content = content
        for i, placeholder in enumerate(reversed(ref_placeholders)):
            if i < len(fig_numbers):
                num = fig_numbers[len(fig_numbers) - 1 - i]
                start, end = placeholder.span()
                new_content = new_content[:start] + f"[@fig:{num}]" + new_content[end:]
        # 4. Удаляем оставшиеся метки {#fig:N}
        new_content = re.sub(rf"\s*{{#{FIGURE_MARKER}:\d+}}", "", new_content)
        # 5. Исправляем пути: Pictures/ -> media/
        new_content = new_content.replace(SOURCE_IMAGE_FOLDER, TARGET_IMAGE_FOLDER)
        return new_content
