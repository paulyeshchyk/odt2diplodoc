import json

from diplodoc_converter.fromODT.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.pipeline.stages.SectionsStage import SectionsStage
from pathlib import Path

from diplodoc_converter.fromODT.pipeline.stages.stage import Stage


class ReplaceCrossLinksStage(Stage):
    def process(self, ctx: ConversionContext) -> None:

        if getattr(ctx.config.pandoc_options, "enable_crossref", False):
            ctx.fig_map = self.load_2_fig_map(ctx)

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
                for sec in SectionsStage.flatten_sections(ctx.sections):
                    if old in sec.body:
                        sec.body = sec.body.replace(old, new)

    def load_fig_map(self, fig_map_path):
        with open(fig_map_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_2_fig_map(self, ctx: ConversionContext):
        # Загружаем fig_map из сохранённого JSON
        temp_odt = (
            Path(ctx.config.cache_settings.temp_dir).absolute()
            / ConverterSettings.TEMP_ODT_FILENAME
        )
        fig_map_path = temp_odt.with_suffix(ConverterSettings.FIG_MAP_EXT)
        if fig_map_path.exists():
            return self.load_fig_map(fig_map_path)
        else:
            print(ctx.messages.get("fig_map_warning"))
            return None
