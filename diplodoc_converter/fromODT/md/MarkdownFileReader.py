from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.os_file_utils import Os_File_Utils


class MarkdownFileReader:
    def read_from_cache(self, ctx: ConversionContext) -> str | None:
        temp_md = Os_File_Utils.md_temp_path(ctx.config)

        cache = ctx.config.cache_settings
        if cache.reuse_cache and temp_md.exists():
            print(ctx.messages.get("using_cache", path=temp_md))
            return temp_md.read_text(encoding="utf-8")
