from pathlib import Path
from diplodoc_converter.fromODT.model.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.stages.MDSectionsStage import SectionFlatten
from .base import Stage


class MDFigureMapReplaceStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Подмена ссылок на фигуры ...")
        if not ctx.config.odt_crossreferences_options.enable_crossref:
            print("Построение карты фигур запрещено: замена отклонена")
            return

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
            for sec in SectionFlatten.flatten_sections(ctx.sections):
                if old in sec.body:
                    sec.body = sec.body.replace(old, new)
