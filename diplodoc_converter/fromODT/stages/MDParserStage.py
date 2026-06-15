from diplodoc_converter.fromODT.md import MarkdownFileReader
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.model_builder.PandocContextBuilder import (
    PandocContextBuilder,
)
from diplodoc_converter.fromODT.pandoc_utils import PandocWrapper

from .base import Stage


class MDParserStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Парсинг MD ...")

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
