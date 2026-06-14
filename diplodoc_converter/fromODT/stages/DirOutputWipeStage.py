import shutil
from pathlib import Path
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from .base import Stage


class DirOutputWipeStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        output_dir = Path(ctx.config.output_dir).absolute()
        if output_dir.exists():
            print(ctx.messages.get("wipe_output"))
            shutil.rmtree(output_dir, ignore_errors=True)
