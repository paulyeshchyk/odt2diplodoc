from pathlib import Path
from typing import no_type_check

from lxml import etree

from diplodoc_converter.fromODT.odt.preprocessors.OdtPreprocessor import OdtPreprocessor
from diplodoc_converter.fromODT.odt.process_odt_delegate import (
    process_odt_with_delegate,
)


class OdtPreprocessor_StyleNote(OdtPreprocessor):
    """
    Находит в ODT блоки с заметками (пользовательскими стилями)
    и заменяет их на текстовые маркеры (placeholders).
    """

    def process(self, odt_path: Path) -> None:
        process_odt_with_delegate(odt_path, self._process_notes)

    NAMESPACES = {"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
    # Стили заметок и соответствующие префиксы маркеров
    NOTE_STYLES = {
        "NoteAlert": "ALERT",
        "NoteInfo": "INFO",
        "NoteTip": "TIP",
    }

    @no_type_check
    def _process_notes(self, tmp_path: Path) -> dict | None:
        content_xml = tmp_path / "content.xml"
        tree = etree.parse(str(content_xml))
        root = tree.getroot()

        note_markers = {"NoteAlert": "ALERT", "NoteInfo": "INFO", "NoteTip": "TIP"}

        stats = {note_type: 0 for note_type in note_markers.values()}

        def extract_text(elem: etree._Element) -> str:
            return "".join(elem.itertext()).strip()

        def is_heading(elem: etree._Element) -> bool:
            """Проверяет, является ли абзац заголовком (содержит жирный span)."""
            # Ищем span с атрибутом text:style-name, содержащим "Strong"
            return bool(
                elem.xpath(
                    './/text:span[contains(@text:style-name, "Strong")]',
                    namespaces=self.NAMESPACES,
                )
            )

        for style, marker_prefix in note_markers.items():
            xpath = f'.//text:p[@text:style-name="{style}"]'
            elems = root.xpath(xpath, namespaces=self.NAMESPACES)
            i = 0
            while i < len(elems):
                elem = elems[i]
                if not is_heading(elem):
                    # Если это не заголовок, пропускаем (не должно быть, но на всякий случай)
                    i += 1
                    continue

                # Заголовок
                title = extract_text(elem).strip()
                body_parts = []
                j = i + 1
                # Собираем тело – следующие абзацы, пока не встретим заголовок
                while j < len(elems) and not is_heading(elems[j]):
                    body_parts.append(extract_text(elems[j]).strip())
                    j += 1

                body = "\n".join(body_parts).strip()
                marker = f"@@@NOTE_{marker_prefix}||{title}||{body}@@@"

                # Заменяем первый абзац (заголовок) на маркер
                first = elems[i]
                # Очищаем дочерние элементы, оставляем только текст
                for child in first:
                    first.remove(child)
                first.text = marker

                # Удаляем все абзацы тела
                for k in range(i + 1, j):
                    parent = elems[k].getparent()
                    if parent is not None:
                        parent.remove(elems[k])

                # Обновляем счётчик обработанных заметок
                stats[marker_prefix] += 1
                # Переходим к следующему заголовку (j указывает на следующий необработанный элемент)
                i = j

        # Сохраняем изменения
        tree.write(str(content_xml), encoding="utf-8", xml_declaration=True)
        return stats
