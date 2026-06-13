# diplodoc_converter/section_strategy/base.py
from abc import ABC, abstractmethod

from diplodoc_converter.fromODT.section_parser import Section


class MDSectionStrategy(ABC):
    @abstractmethod
    def transform_section(self, sec: Section) -> None:
        """Модифицирует `sec.body` на месте."""
        pass
