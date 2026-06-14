from dataclasses import dataclass


@dataclass
class PyPandocContext:
    source_file: str
    pandoc_fmt: str
    output_fmt: str
    extra_args: list[str]
    outputfile: str
