from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.context.context_utils import get_temp_md


class MarkdownFileReader:
    def read_from_cache(self, ctx: ConversionContext) -> str | None:
        temp_md = get_temp_md(ctx)

        cache = ctx.config.cache_settings
        if cache.reuse_cache and temp_md.exists():
            print(ctx.messages.get("using_cache", path=temp_md))
            return temp_md.read_text(encoding="utf-8")
