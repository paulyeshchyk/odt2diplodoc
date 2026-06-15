from diplodoc_converter.fromODT.model import CacheSettings, ConverterMessages
from diplodoc_converter.fromODT.model_builder.ConfigBuilder import ConfigBuilder
from diplodoc_converter.fromODT.pipeline import Pipeline
from diplodoc_converter.fromODT.stages import (
    DirCacheWipeStage,
    DirOutputWipeStage,
    GlobalStrategiesStage,
    MDFigureMapReplaceStage,
    MDParserStage,
    MDSectionCopyImagesStage,
    MDSectionsLinkProcessingStage,
    MDSectionsStage,
    MDSectionStrategiesStage,
    ODTCloneStage,
    ODTFigureMapBuildStage,
    ODTPagebrakeReplaceStage,
    ODTStyleNoteReplaceStage,
    YamlStage,
)


class cli_odt2md:
    @staticmethod
    def run_import(args):
        messages = ConverterMessages(lang="ru")

        config_builder = ConfigBuilder()
        ctx = config_builder.build_conversion_context(args, messages)
        if ctx.config.cache_settings is None:
            ctx.config.cache_settings = CacheSettings()

        pipeline = Pipeline(
            [
                DirOutputWipeStage(),
                ODTCloneStage(),
                ODTFigureMapBuildStage(),
                ODTStyleNoteReplaceStage(),
                ODTPagebrakeReplaceStage(),
                MDParserStage(),
                GlobalStrategiesStage(),
                MDSectionsStage(),
                MDSectionsLinkProcessingStage(),
                MDSectionCopyImagesStage(),
                MDFigureMapReplaceStage(),
                MDSectionStrategiesStage(),
                YamlStage(),
                DirCacheWipeStage(),
            ]
        )
        pipeline.run(ctx)
