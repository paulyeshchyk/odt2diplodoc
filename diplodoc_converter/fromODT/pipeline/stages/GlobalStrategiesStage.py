from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.pipeline.stages.stage import Stage
from diplodoc_converter.fromODT.strategies import global_strategies


class GlobalStrategiesStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        for strategy in global_strategies:
            ctx.markdown = strategy.transform(ctx.markdown)
