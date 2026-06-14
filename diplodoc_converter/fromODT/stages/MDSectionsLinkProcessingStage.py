from pathlib import Path
from diplodoc_converter.fromODT.link_processor import (
    build_slug_and_anchor_maps,
    replace_internal_links,
)
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.stages.MDSectionsStage import MDSectionsStage

from .base import Stage


class MDSectionsLinkProcessingStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print(ctx.messages.get("internal_links"))
        output_dir = Path(ctx.config.output_dir).absolute()

        slug_map, anchor_map = build_slug_and_anchor_maps(ctx.sections, output_dir)
        for sec in MDSectionsStage.flatten_sections(ctx.sections):
            sec.body = replace_internal_links(
                sec.body, slug_map, anchor_map, str(sec.full_slug).replace("\\", "/")
            )
