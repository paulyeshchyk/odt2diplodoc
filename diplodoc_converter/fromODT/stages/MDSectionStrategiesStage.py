from diplodoc_converter.fromODT.md.strategies import section_strategies
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.stages.MDSectionsStage import SectionFlatten

from .base import Stage


class MDSectionStrategiesStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Запуск стратегий обработки секций ...")
        for strategy in section_strategies:
            for sec in SectionFlatten.flatten_sections(ctx.sections):
                strategy.transform_section(sec)
