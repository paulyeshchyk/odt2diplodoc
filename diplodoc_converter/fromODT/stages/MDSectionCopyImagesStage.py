from pathlib import Path

from diplodoc_converter.fromODT.image_processor import extract_and_replace_images
from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.model.ConverterSettings import ConverterSettings
from diplodoc_converter.fromODT.model.Section import Section

from .base import Stage


class MDSectionCopyImagesStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print(ctx.messages.get("copying_images"))

        output_root = Path(ctx.config.output_dir).absolute()
        temp_media_dir = (
            Path(ctx.config.cache_settings.temp_dir).absolute()
            / ConverterSettings.MEDIA_DIR
        )

        def process(sec: Section, current_path: Path):
            target_images_dir = current_path / ConverterSettings.MEDIA_DIR
            new_body, _ = extract_and_replace_images(
                sec.body, temp_media_dir, target_images_dir
            )
            sec.body = new_body
            for child in sec.children:
                process(child, current_path / child.slug)

        if ctx.sections:
            for sec in ctx.sections:
                process(sec, output_root / sec.slug)
