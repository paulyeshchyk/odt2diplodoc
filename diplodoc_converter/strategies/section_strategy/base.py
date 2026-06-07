# diplodoc_converter/section_strategy/base.py
from abc import ABC, abstractmethod

from diplodoc_converter.section_parser import Section


class SectionStrategy(ABC):
    @abstractmethod
    def transform_section(self, sec: Section) -> None:
        """Модифицирует `sec.body` (и, возможно, другие поля) на месте."""
        pass