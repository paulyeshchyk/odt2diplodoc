from typing import List

from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.pipeline.stages.stage import Stage


class Pipeline:
    def __init__(self, stages: List[Stage]):
        self.stages = stages

    def run(self, ctx: ConversionContext) -> None:
        for stage in self.stages:
            stage.process(ctx)
