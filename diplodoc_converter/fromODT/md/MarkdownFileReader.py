from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.utils import Conversion_File_Utils


class MarkdownFileReader:
    def read_from_cache(self, ctx: ConversionContext) -> str | None:
        temp_md = Conversion_File_Utils.md_temp_path(ctx.config)

        cache = ctx.config.cache_settings
        if cache.reuse_cache and temp_md.exists():
            print(ctx.messages.get("using_cache", path=temp_md))
            return temp_md.read_text(encoding="utf-8")
        return None
