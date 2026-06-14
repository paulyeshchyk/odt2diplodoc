from diplodoc_converter.intoODT.config import MdToOdtConfig


class cli_export:
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
        from diplodoc_converter.intoODT.cli import run

        run()
