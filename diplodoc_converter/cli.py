import argparse

from diplodoc_converter.cli_args_builder import cli_args_builder
from diplodoc_converter.fromODT.cli_odt2md import cli_odt2md
from diplodoc_converter.intoODT.cli_md2odt import cli_md2odt


def main():
    parser = argparse.ArgumentParser(
        description="Diplodoc Converter: импорт ODT в MD или сборка ODT из MD"
    )
    args = cli_args_builder.build_args(parser)

    if args.command == "import":
        cli_odt2md.run_import(args)
    elif args.command == "build":
        cli_md2odt.run_export(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
