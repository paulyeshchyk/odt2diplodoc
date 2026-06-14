from dataclasses import dataclass
from typing import List, Optional
from diplodoc_converter.fromODT.model import ConverterMessages
from diplodoc_converter.fromODT.model.ConversionConfig import ConversionConfig
from diplodoc_converter.fromODT.model.Section import Section


@dataclass
class ConversionContext:
    config: ConversionConfig
    messages: ConverterMessages
    markdown: Optional[str] = None
    sections: Optional[List[Section]] = None
    fig_map: Optional[dict] = None
