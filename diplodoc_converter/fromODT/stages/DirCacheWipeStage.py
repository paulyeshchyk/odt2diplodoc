from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from .Stage import Stage


import shutil
from pathlib import Path


class DirCacheWipeStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        temp_dir = Path(ctx.config.cache_settings.temp_dir).absolute()
        if not ctx.config.cache_settings.keep_cache and temp_dir.exists():
            print(ctx.messages.get("wipe_cache"))
            shutil.rmtree(temp_dir, ignore_errors=True)
        elif ctx.config.cache_settings.keep_cache and temp_dir.exists():
            print(ctx.messages.get("cache_kept", path=temp_dir))
