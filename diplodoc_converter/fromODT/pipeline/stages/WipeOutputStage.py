from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.pipeline.stages.stage import Stage
from pathlib import Path

import shutil


class WipeOutputStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        output_dir = Path(ctx.config.output_dir).absolute()
        if output_dir.exists():
            print(ctx.messages.get("wipe_output"))
            shutil.rmtree(output_dir, ignore_errors=True)
