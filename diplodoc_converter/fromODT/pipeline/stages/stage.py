from abc import ABC

from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext


class Stage(ABC):
    def process(self, ctx: ConversionContext) -> None:
        pass
