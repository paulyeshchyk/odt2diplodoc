import re
from diplodoc_converter.fromODT.section_parser import Section
from diplodoc_converter.fromODT.md.strategies.section.MDSectionStrategy import (
    MDSectionStrategy,
)


class MDSectionStrategyImagesInFiguresWrap(MDSectionStrategy):
    def transform_section(self, sec: Section) -> None:
        sec.body = self._transform_body(sec.body)

    def _transform_body(self, content: str) -> str:
        pattern = re.compile(
            r'!\[(.*?)\]\((images|media)/([^)]+)\)\s*(\{alt=("|\')(.*?)\5\})?',
            re.DOTALL,
        )

        def repl(m):
            short_alt = m.group(1).strip()
            folder = m.group(2)
            filename = m.group(3)
            full_alt = m.group(6) if m.group(6) else short_alt
            # Очистка экранирования
            full_alt = full_alt.replace(r"\"", '"').replace(r"\&quot;", '"')
            full_alt = re.sub(r"\\([\[\]])", r"\1", full_alt)
            # Добавляем пробел после "Рисунок 12." если его нет
            full_alt = re.sub(r"(Рисунок\s+\d+\.)(\S)", r"\1 \2", full_alt)
            # Удаляем все лишние пробелы и переводы строк (заменяем на один пробел)
            full_alt = re.sub(r"\s+", " ", full_alt).strip()
            src = f"{folder}/{filename}"
            if not full_alt:
                # Пустая подпись – не добавляем звёздочки
                return f"![{short_alt}]({src})\n\n"
            else:
                return f"![{full_alt}]({src})\n\n*{full_alt}*\n\n"

        new_content = pattern.sub(repl, content)
        # new_content = re.sub(r'\{alt=["\'][^"\']*["\']\}', '', new_content)
        return new_content
