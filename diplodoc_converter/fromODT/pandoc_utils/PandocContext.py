from dataclasses import dataclass
from pathlib import Path


@dataclass
class PandocContext:
    odt_path: Path
    temp_md_path: Path
    temp_media_dir: Path
