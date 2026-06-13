import json

from diplodoc_converter.fromODT.context.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.odt.preprocessors.OdtProcessor_CrossRef import (
    OdtProcessor_CrossRef,
)
from diplodoc_converter.fromODT.os_file_utils import Os_File_Utils
from .Stage import Stage


class ODTCrossrefStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        enable_crossref = getattr(
            ctx.config.odt_crossreferences_options, "enable_crossref", False
        )
        if not enable_crossref:
            return

        odt_temp_path = Os_File_Utils.odt_temp_path(ctx.config)

        crossrefProcessor = OdtProcessor_CrossRef()
        ctx.fig_map = crossrefProcessor.process_odt_crossrefs(odt_temp_path)

        fig_map_path = Os_File_Utils.odt_figmap_temp_path(ctx.config)
        with open(fig_map_path, "w", encoding="utf-8") as f:
            json.dump(ctx.fig_map, f)
