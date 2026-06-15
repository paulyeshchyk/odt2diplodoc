import os
from pathlib import Path

import pypandoc  # type: ignore

from diplodoc_converter.fromODT.model_builder.PyPandocContextBuilder import (
    PyPandocContextBuilder,
)

from .PandocContext import PandocContext
from .PandocOptions import PandocOptions


class PandocWrapper:
    def convert_odt_to_markdown(
        self,
        pandoc_ctx: PandocContext,
        pandoc_options: PandocOptions,
    ) -> str:
        # Os_File_Utils.ensure_dir(pandoc_ctx.temp_media_dir)

        original_cwd = Path.cwd()
        pyPandocContextBuilder = PyPandocContextBuilder()
        pyPandocContext = pyPandocContextBuilder.build(
            original_cwd,
            pandoc_ctx,
            pandoc_options,
        )

        target_dir = pandoc_ctx.temp_media_dir.parent
        os.chdir(target_dir)
        try:
            pypandoc.convert_file(
                source_file=pyPandocContext.source_file,
                to=pyPandocContext.pandoc_fmt,
                format=pyPandocContext.output_fmt,
                extra_args=pyPandocContext.extra_args,
                outputfile=pyPandocContext.outputfile,
            )
            result = pandoc_ctx.temp_md_path.read_text(encoding="utf-8")
        finally:
            os.chdir(original_cwd)
        return result
