from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.odt.preprocessors.OdtProcessor_CrossRef import (
    OdtProcessor_CrossRef,
)
from diplodoc_converter.fromODT.utils import Conversion_File_Utils

from .base import Stage


class ODTFigureMapBuildStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Построение карты фигур ...")

        if not ctx.config.odt_crossreferences_options.enable_crossref:
            print("Построение карты фигур Прервано")
            return

        odt_temp_path = Conversion_File_Utils.odt_temp_path(ctx.config)

        crossrefProcessor = OdtProcessor_CrossRef()
        ctx.fig_map = crossrefProcessor.process_odt_crossrefs(odt_temp_path)
