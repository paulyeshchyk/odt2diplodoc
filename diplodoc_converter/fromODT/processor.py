from abc import ABC
from typing import Any

from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext


class Processor(ABC):
    def apply(self, data: Any, ctx: ConversionContext) -> Any:
        pass
