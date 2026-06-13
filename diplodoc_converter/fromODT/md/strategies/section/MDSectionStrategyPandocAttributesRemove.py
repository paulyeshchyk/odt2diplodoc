# diplodoc_converter/section_strategy/remove_pandoc_attrs.py
import re

from diplodoc_converter.fromODT.section_parser import Section
from diplodoc_converter.fromODT.md.strategies.section.MDSectionStrategy import (
    MDSectionStrategy,
)


class MDSectionStrategyPandocAttributesRemove(MDSectionStrategy):
    def transform_section(self, sec: Section) -> None:
        sec.body = self.transform(sec.body)

    def transform(self, content: str) -> str:
        # Удаляет {alt="..."} и {alt='...'} с учётом экранированных кавычек внутри
        pattern = r'\{alt=("|\')(?:[^\\]|\\.)*?\1\}'
        # multi-line не обязателен, так как точечный шаблон с \n работает
        content = re.sub(pattern, "", content, flags=re.DOTALL)
        # Удаляем возможные пустые строки
        content = re.sub(r"\n\s*\n", "\n\n", content)
        return content
