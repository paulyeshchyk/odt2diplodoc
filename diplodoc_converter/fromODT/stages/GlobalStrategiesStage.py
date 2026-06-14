from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from .base import Stage
from diplodoc_converter.fromODT.md.strategies import global_strategies


class GlobalStrategiesStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Запуск глобальных стратегий ...")
        for strategy in global_strategies:
            ctx.markdown = strategy.transform(ctx.markdown or "")
