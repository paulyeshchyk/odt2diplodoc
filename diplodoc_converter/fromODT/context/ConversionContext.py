from dataclasses import dataclass
from typing import List, Optional
from diplodoc_converter.fromODT.ConverterMessages import ConverterMessages
from diplodoc_converter.fromODT.config import ConversionConfig
from diplodoc_converter.fromODT.section_parser import Section


@dataclass
class ConversionContext:
    config: ConversionConfig
    messages: ConverterMessages
    markdown: Optional[str] = None
    sections: Optional[List[Section]] = None
    fig_map: Optional[dict] = None
