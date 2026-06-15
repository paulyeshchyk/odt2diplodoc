from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set

from diplodoc_converter.intoODT.models import DocNode


@dataclass
class ProcessingContext:
    root_dir: Path
    temp_dir: Path
    anchor_map: Dict[Path, str]
    current_node: DocNode
    content: str
    used_anchors: Set[str] = field(default_factory=set)
