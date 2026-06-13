from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.os_file_utils import Os_File_Utils


import json


class JsonUtils:
    @staticmethod
    def load_figmap(ctx: ConversionContext):
        # Загружаем fig_map из сохранённого JSON

        fig_map_path = Os_File_Utils.odt_figmap_temp_path(ctx.config)
        if fig_map_path.exists():
            with open(fig_map_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(ctx.messages.get("fig_map_warning"))
            return None

    @staticmethod
    def dump_figmap(ctx):
        fig_map_path = Os_File_Utils.odt_figmap_temp_path(ctx.config)
        with open(fig_map_path, "w", encoding="utf-8") as f:
            json.dump(ctx.fig_map, f)
