from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.pipeline.stages.SectionsStage import SectionsStage
from diplodoc_converter.fromODT.pipeline.stages.stage import Stage
from diplodoc_converter.fromODT.strategies import section_strategies


class SectionStrategiesStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        for strategy in section_strategies:
            for sec in SectionsStage.flatten_sections(ctx.sections):
                strategy.transform_section(sec)
