import json
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.utils import Conversion_File_Utils


class JsonUtils:
    @staticmethod
    def load_figmap(ctx: ConversionContext):
        # Загружаем fig_map из сохранённого JSON

        fig_map_path = Conversion_File_Utils.odt_figmap_temp_path(ctx.config)
        if fig_map_path.exists():
            with open(fig_map_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(ctx.messages.get("fig_map_warning"))
            return None

    @staticmethod
    def dump_figmap(ctx):
        fig_map_path = Conversion_File_Utils.odt_figmap_temp_path(ctx.config)
        with open(fig_map_path, "w", encoding="utf-8") as f:
            json.dump(ctx.fig_map, f)
