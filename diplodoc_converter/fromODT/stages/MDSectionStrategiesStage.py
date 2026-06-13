from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.stages.MDSectionsStage import MDSectionsStage
from .Stage import Stage
from diplodoc_converter.fromODT.md.strategies import section_strategies


class MDSectionStrategiesStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        for strategy in section_strategies:
            for sec in MDSectionsStage.flatten_sections(ctx.sections):
                strategy.transform_section(sec)
