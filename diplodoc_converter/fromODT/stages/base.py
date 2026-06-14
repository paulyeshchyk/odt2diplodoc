from abc import ABC

from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext


class Stage(ABC):
    def process(self, ctx: ConversionContext) -> None:
        pass
