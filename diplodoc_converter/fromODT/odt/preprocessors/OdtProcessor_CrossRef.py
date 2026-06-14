from pathlib import Path
from typing import no_type_check
from lxml import etree

from diplodoc_converter.fromODT.odt.process_odt_delegate import (
    process_odt_with_delegate,
)

from ...model.figure_constants import FIGURE_PREFIX, FIGURE_MARKER

NAMESPACES = {
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}


class OdtProcessor_CrossRef:
    @no_type_check
    def process_odt_crossrefs(self, odt_path: Path) -> dict:
        def _process(tmp_path: Path) -> dict:
            content_xml = tmp_path / "content.xml"
            tree = etree.parse(str(content_xml))
            root = tree.getroot()

            fig_map = {}
            ref_map = {}

            # Этап 1: сбор рисунков и добавление меток {#fig:N}
            for frame in root.xpath(".//draw:frame", namespaces=NAMESPACES):
                seq = frame.find(".//text:sequence", namespaces=NAMESPACES)
                if seq is None:
                    continue
                num = seq.text.strip()  # type: ignore[arg-type]
                ref_name = seq.get(f"{{{NAMESPACES['text']}}}ref-name")
                if ref_name:
                    ref_map[ref_name] = num
                img = frame.find(".//draw:image", namespaces=NAMESPACES)
                if img is not None:
                    img_href = img.get(f"{{{NAMESPACES['xlink']}}}href")
                    fig_map[num] = img_href

                # Добавляем метку {#fig:N} в подпись
                para = seq
                while para is not None and para.tag != f"{{{NAMESPACES['text']}}}p":
                    para = para.getparent()
                if para is not None:
                    current_text = etree.tostring(
                        para, encoding="unicode", method="text"
                    )
                    marker = f"{{#{FIGURE_MARKER}:{num}}}"
                    if marker not in current_text:
                        span = etree.Element(f"{{{NAMESPACES['text']}}}span")
                        span.text = f" {marker}"
                        para.append(span)

            # Этап 2: замена sequence-ref на (рис. N)
            for seq_ref in root.xpath(".//text:sequence-ref", namespaces=NAMESPACES):
                ref_name = seq_ref.get(f"{{{NAMESPACES['text']}}}ref-name")
                if ref_name and ref_name in ref_map:
                    num = ref_map[ref_name]
                    parent = seq_ref.getparent()
                    new_span = etree.Element(f"{{{NAMESPACES['text']}}}span")
                    new_span.text = f"({FIGURE_PREFIX} {num})"
                    parent.replace(seq_ref, new_span)

            tree.write(str(content_xml), encoding="utf-8", xml_declaration=True)
            assert len(fig_map.keys()) != 0, "Не найдены кросс-ссылки"
            print(f"Обработано кросс-ссылок: {len(fig_map.keys())}")
            return fig_map

        return process_odt_with_delegate(odt_path, _process)
