# cli_export.py

import sys
from pathlib import Path

from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.postProcessing.odt_builder import OdtBuilderPipeline
from diplodoc_converter.intoODT.stages import (
    AnchorMappingStep,
    ImageCopyingStep,
    MarkdownCompilationStep,
    OdtPostProcessingStep,
    PandocConversionStep,
    TocParsingStep,
)


class cli_md2odt:
    @staticmethod
    def run_export(args):
        MdToOdtConfig.update(
            DEFAULT_INPUT_DIR=args.input_dir,
            DEFAULT_OUTPUT_FILE=args.output,
            REFERENCE_ODT=args.reference,
            WIDTH_THRESHOLD=args.width_threshold,
            MAX_HEADING_LEVEL=args.max_heading,
            CAPTION_POSITION=args.caption_position,
        )

        """Запускает сборку ODT, используя текущие настройки MdToOdtConfig."""
        input_dir = Path(MdToOdtConfig.DEFAULT_INPUT_DIR)
        if not input_dir.is_dir():
            print(f"Директория {input_dir} не найдена")
            sys.exit(1)

        root_dir = input_dir.resolve()
        root_toc = root_dir / "toc.yaml"
        if not root_toc.is_file():
            print(f"Не найден {root_toc}")
            sys.exit(1)

        output_file = Path(MdToOdtConfig.DEFAULT_OUTPUT_FILE).resolve()

        try:
            steps = [
                TocParsingStep(),
                AnchorMappingStep(),
                ImageCopyingStep(),
                MarkdownCompilationStep(),
                PandocConversionStep(),
                OdtPostProcessingStep(),
            ]

            builder = OdtBuilderPipeline(steps)
            builder.build(root_dir, output_file)
        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)
