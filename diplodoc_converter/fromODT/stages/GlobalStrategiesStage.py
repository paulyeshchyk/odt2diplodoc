from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from .Stage import Stage
from diplodoc_converter.fromODT.md.strategies import global_strategies


class GlobalStrategiesStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        for strategy in global_strategies:
            ctx.markdown = strategy.transform(ctx.markdown)
