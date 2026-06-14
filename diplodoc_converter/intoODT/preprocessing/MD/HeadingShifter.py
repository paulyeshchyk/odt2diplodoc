from diplodoc_converter.intoODT.Transliterator import Transliterator
from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.postProcessing.MD.ProcessingContext import (
    ProcessingContext,
)


import re
from typing import Set


class HeadingShifter:
    used_anchors: Set[str] = set()

    def process(self, ctx: ProcessingContext) -> None:
        self.used_anchors = ctx.used_anchors
        if not ctx.current_node.rel_path:
            return
        node_anchor = ctx.anchor_map.get(ctx.current_node.rel_path, "doc")
        ctx.content = self._shift_headings(
            ctx.content, ctx.current_node.level, node_anchor
        )

    def _shift_headings(self, content: str, node_level: int, node_anchor: str) -> str:
        shift = node_level + 1

        def replacer(match):
            hashes = match.group(1)
            title_text = match.group(2).strip()
            new_level = min(len(hashes) + shift, MdToOdtConfig.MAX_HEADING_LEVEL)
            sub_anchor = Transliterator.transliterate(title_text.lower()).replace(
                " ", "-"
            )
            sub_anchor = re.sub(r"[^a-zA-Z0-9_.-]", "_", sub_anchor)
            full_heading_id = f"{node_anchor}_{sub_anchor}"
            # Защита от дубликатов
            if full_heading_id in self.used_anchors:
                counter = 1
                new_id = f"{full_heading_id}_{counter}"
                while new_id in self.used_anchors:
                    counter += 1
                    new_id = f"{full_heading_id}_{counter}"
                full_heading_id = new_id
            self.used_anchors.add(full_heading_id)
            return f"{'#' * new_level} {title_text} {{#{full_heading_id} .unnumbered}}"

        pattern = r"^(#{1,6})\s+(.+)$"
        return re.sub(pattern, replacer, content, flags=re.MULTILINE)
