from pathlib import Path
from typing import no_type_check

from lxml import etree

from diplodoc_converter.fromODT.odt.process_odt_delegate import (
    process_odt_with_delegate,
)

from .OdtPreprocessor import OdtPreprocessor


class OdtPreprocessor_PageBreak(OdtPreprocessor):
    @no_type_check
    def process(self, odt_path: Path) -> None:
        """Заменяет разрывы страниц в ODT на маркеры."""
        process_odt_with_delegate(odt_path, self._process_page_breaks)

    NAMESPACES = {
        "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    }

    @no_type_check
    def _process_page_breaks(self, tmp_path: Path) -> dict | None:
        content_xml = tmp_path / "content.xml"
        tree = etree.parse(str(content_xml))
        root = tree.getroot()

        count = 0

        # 1. Ищем абзацы со стилем, содержащим "PageBreak" (например, "PageBreak")
        xpath1 = './/text:p[contains(@text:style-name, "PageBreak")]'
        for elem in root.xpath(xpath1, namespaces=self.NAMESPACES):
            if not elem.text or elem.text.strip() == "":
                elem.text = "@@@PAGE_BREAK@@@"
                # Очищаем дочерние элементы
                for child in elem:
                    elem.remove(child)
                count += 1

        # 2. Ищем абзацы с атрибутом fo:break-before="page"
        xpath2 = './/text:p[@fo:break-before="page"]'
        for elem in root.xpath(xpath2, namespaces=self.NAMESPACES):
            elem.attrib.pop(
                "{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}break-before",
                None,
            )
            elem.text = "@@@PAGE_BREAK@@@"
            for child in elem:
                elem.remove(child)
            count += 1

        # 3. Пустые абзацы с определённым стилем (например, "PN", где N - число)
        for elem in root.xpath(".//text:p", namespaces=self.NAMESPACES):
            style_name = elem.get(f"{{{self.NAMESPACES['text']}}}style-name")
            if (
                style_name
                and len(style_name) > 1
                and style_name[0] == "P"
                and style_name[1:].isdigit()
            ):
                if (elem.text is None or elem.text.strip() == "") and len(elem) == 0:
                    elem.text = "@@@PAGE_BREAK@@@"
                    count += 1

        # 4 (Опционально) Ищем пустые абзацы с пометкой "Page Break" в тексте
        # Можно добавить дополнительные условия при необходимости

        if count > 0:
            tree.write(str(content_xml), encoding="utf-8", xml_declaration=True)

        return {"page_breaks": count}
