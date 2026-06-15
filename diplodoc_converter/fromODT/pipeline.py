from typing import List

from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext

from .stages.base import Stage


class Pipeline:
    def __init__(self, stages: List[Stage]):
        self.stages = stages

    def run(self, ctx: ConversionContext) -> None:
        for stage in self.stages:
            stage.process(ctx)
