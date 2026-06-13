from diplodoc_converter.fromODT.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.stages.MDSectionsStage import MDSectionsStage
from pathlib import Path

from .Stage import Stage


class MDFigureMapReplaceStage(Stage):
    def process(self, ctx: ConversionContext) -> None:

        if getattr(ctx.config.odt_crossreferences_options, "enable_crossref", False):
            # нет больше необходимости читать из json
            # ctx.fig_map = self.load_2_fig_map(ctx)

            if not ctx.fig_map:
                print(ctx.messages.get("fig_map_empty_warning"))
                return

            media_paths = {
                num: f"{ConverterSettings.MEDIA_DIR}/{Path(src_path).name}"
                for num, src_path in ctx.fig_map.items()
            }

            for num, media_path in media_paths.items():
                old = f"[@fig:{num}]"
                new = f"[{num}]({media_path})"
                for sec in MDSectionsStage.flatten_sections(ctx.sections):
                    if old in sec.body:
                        sec.body = sec.body.replace(old, new)
