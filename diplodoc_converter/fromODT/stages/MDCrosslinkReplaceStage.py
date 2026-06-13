import json

from diplodoc_converter.fromODT.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.os_file_utils import Os_File_Utils
from diplodoc_converter.fromODT.stages.MDSectionsStage import MDSectionsStage
from pathlib import Path

from .Stage import Stage


class MDCrosslinkReplaceStage(Stage):
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

    def load_fig_map(self, fig_map_path):
        with open(fig_map_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_2_fig_map(self, ctx: ConversionContext):
        # Загружаем fig_map из сохранённого JSON

        fig_map_path = Os_File_Utils.odt_figmap_temp_path(ctx.config)
        if fig_map_path.exists():
            return self.load_fig_map(fig_map_path)
        else:
            print(ctx.messages.get("fig_map_warning"))
            return None
