# ============================================================
# 1. КОНТЕКСТ ПАЙПЛАЙНА
# ============================================================
from pathlib import Path
from typing import Dict, List

from diplodoc_converter.intoODT.models import DocNode


class OdtBuildContext:
    """Контекст сборки, хранящий изменяемое состояние между этапами пайплайна."""

    def __init__(self, root_dir: Path, output_path: Path):
        # Входные параметры
        self.root_dir: Path = root_dir
        self.output_path: Path = output_path

        # Промежуточное состояние, наполняемое шагами пайплайна
        self.nodes: List[DocNode] = []  # Заполнится на этапе TocParsingStep
        self.anchor_map: Dict[Path, str] = {}
        self.temp_dir: Path = Path()
        self.combined_md_path: Path = Path()
