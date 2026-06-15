import re
from pathlib import Path
from typing import Dict, List

from diplodoc_converter.intoODT.models import DocNode
from diplodoc_converter.intoODT.stages.OdtBuildContext import OdtBuildContext
from diplodoc_converter.intoODT.stages.OdtPipelineStep import OdtPipelineStep
from diplodoc_converter.intoODT.Transliterator import Transliterator


class AnchorMappingStep(OdtPipelineStep):
    """Шаг 1: Построение карты уникальных якорей (якори для перекрестных ссылок)."""

    def execute(self, context: OdtBuildContext) -> None:
        if not context.nodes:
            return
        self._build_anchor_map(context.nodes, context.anchor_map)
        print(f"[Pipeline]: Карта якорей построена ({len(context.anchor_map)} эл.)")

    def _build_anchor_map(self, nodes: List[DocNode], anchor_map: Dict[Path, str]):
        for node in nodes:
            if node.rel_path:
                anchor_map[node.rel_path] = self._generate_anchor(node.rel_path)
            if node.children:
                self._build_anchor_map(node.children, anchor_map)

    @staticmethod
    def _generate_anchor(rel_path: Path) -> str:
        parts = rel_path.with_suffix("").parts
        anchor = "_".join(parts)
        anchor = Transliterator.transliterate(anchor)
        anchor = re.sub(r"[^a-zA-Z0-9_.-]", "_", anchor)
        return f"doc_{anchor}"
