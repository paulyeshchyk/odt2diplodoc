from dataclasses import dataclass
from typing import Optional


@dataclass
class OdtCrossReferences:
    enable_crossref: bool = False
    crossref_metadata_file: Optional[str] = None
