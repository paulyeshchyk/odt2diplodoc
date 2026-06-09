import re
from diplodoc_converter.figure_constants import CAPTION_SEPARATOR, FIGURE_CAPTION_PREFIX, TARGET_IMAGE_FOLDER
from diplodoc_converter.section_parser import Section
from diplodoc_converter.strategies.section_strategy.base import SectionStrategy

class WrapImagesInFiguresStrategy(SectionStrategy):
    def transform_section(self, sec: Section) -> None:
        sec.body = self._transform_body(sec.body)

    def _transform_body(self, content: str) -> str:
        pattern = re.compile(
            r'!\[(.*?)\]\((images|media)/([^)]+)\)\s*(\{alt=("|\')(.*?)\5\})?',
            re.DOTALL
        )

        def repl(m):
            short_alt = m.group(1).strip()
            folder = m.group(2)
            filename = m.group(3)
            full_alt = m.group(6) if m.group(6) else short_alt
            # Очистка экранирования
            full_alt = full_alt.replace(r'\"', '"').replace(r"\&quot;", '"')
            full_alt = re.sub(r'\\([\[\]])', r'\1', full_alt)
            # Добавляем пробел после "Рисунок 12." если его нет
            full_alt = re.sub(rf'({FIGURE_CAPTION_PREFIX}\s+\d+\.)(\S)', rf'\1{CAPTION_SEPARATOR}\2', full_alt)
            src = f"{TARGET_IMAGE_FOLDER}/{filename}"
            return f"![{full_alt}]({src})\n\n*{full_alt}*\n\n"

        new_content = pattern.sub(repl, content)
        # new_content = re.sub(r'\{alt=["\'][^"\']*["\']\}', '', new_content)
        return new_content