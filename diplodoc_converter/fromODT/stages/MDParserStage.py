from diplodoc_converter.PandocWrapper import PandocWrapper
from diplodoc_converter.fromODT.builder.PandocContextBuilder import PandocContextBuilder
from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.md import MarkdownFileReader
from .Stage import Stage


class MDParserStage(Stage):
    def process(self, ctx: ConversionContext) -> None:

        markdown_reader = MarkdownFileReader()
        ctx.markdown = markdown_reader.read_from_cache(ctx)
        if not (ctx.markdown):
            pandocWrapper = PandocWrapper()
            try:
                pandoc_context_builder = PandocContextBuilder()
                pandoc_context = pandoc_context_builder.build(ctx)
                ctx.markdown = pandocWrapper.convert_odt_to_markdown(
                    pandoc_context,
                    ctx.config.pandoc_options,
                )
            except Exception as e:
                print(ctx.messages.get("pandoc_error", error=e))
                raise
