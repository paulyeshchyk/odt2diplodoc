from diplodoc_converter.fromODT.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.config import ConversionConfig


import os
from pathlib import Path


class Os_File_Utils:
    @staticmethod
    def odt_temp_path(config: ConversionConfig) -> Path:
        temp_dir = Path(config.cache_settings.temp_dir).absolute()
        return temp_dir / os.path.basename(config.odt_path)

    @staticmethod
    def odt_figmap_temp_path(config: ConversionConfig) -> Path:
        odt_temp_path = Os_File_Utils.odt_temp_path(config)
        return odt_temp_path.with_suffix(ConverterSettings.FIG_MAP_EXT)

    @staticmethod
    def odt_temp_media_path(config: ConversionConfig) -> Path:
        temp_dir = Path(config.cache_settings.temp_dir).absolute()
        return temp_dir / ConverterSettings.MEDIA_DIR

    @staticmethod
    def make_temp_dir(config: ConversionConfig):
        temp_dir = Path(config.cache_settings.temp_dir).absolute()
        os.makedirs(temp_dir, exist_ok=True)

    @staticmethod
    def md_temp_path(config: ConversionConfig) -> Path:
        temp_dir = Path(config.cache_settings.temp_dir).absolute()
        return temp_dir / ConverterSettings.TEMP_MD_FILENAME
