from diplodoc_converter.intoODT.postProcessing.ODT.PandocInjector import PandocInjector
from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.postProcessing.ODT.CrossReferenceManager import (
    CrossReferenceManager,
)


import re


class CrossReferenceStrategy:
    # Замена ссылок Pandoc на ссылки LibreOffice
    def process(self, content_str: str) -> str:
        figure_map = CrossReferenceManager.id_to_ref_map
        if not figure_map:
            print("  [CrossReferenceStrategy] Карта пуста, ссылки не изменены.")
            return content_str

        print("[CrossReferenceStrategy]: Начат")
        count = 0
        seq_name = MdToOdtConfig.CAPTION_SEQUENCE_NAME

        # Паттерн для поиска ссылок Pandoc
        pattern_link = (
            r'(<text:a[^>]*xlink:href="#([^"]*fig-[^"]+)"[^>]*>)(.*?)(</text:a>)'
        )

        def ref_replacer(match):
            nonlocal count
            tag_open = match.group(1)
            full_fig_id = match.group(2)

            # Тут может быть <text:span...>(рис. 1)</text:span>
            raw_link_text = match.group(3)
            tag_close = match.group(4)

            ref_name = figure_map.get(full_fig_id)

            if ref_name:
                count += 1

                # 1. Очищаем текст ссылки от внутренних XML-тегов, чтобы распарсить сам текст (например, "(рис. 1)")
                clean_text = re.sub(r"<[^>]+>", "", raw_link_text).strip()

                # 2. Ищем цифру в тексте ссылки
                digit_match = re.search(r"\d+", clean_text)

                if digit_match:
                    full_digit = digit_match.group(0)  # Сама цифра (например, "1")
                    start_pos, end_pos = digit_match.span()

                    # Выделяем то, что шло ДО цифры ("(рис. ") и ПОСЛЕ (")")
                    prefix_text = clean_text[:start_pos]
                    suffix_text = clean_text[end_pos:]

                    # Если внутри исходной ссылки были стили (например, text:style-name="Definition"),
                    # мы вытащим этот стиль, чтобы сохранить оригинальное оформление техписа
                    style_attr = ""
                    style_match = re.search(r'text:style-name="([^"]+)"', raw_link_text)
                    if style_match:
                        style_attr = f' text:style-name="{style_match.group(1)}"'

                    # 3. Собираем обертку: текст снаружи, поле со ссылкой внутри
                    return PandocInjector.text_sequence_suffix(
                        ref_name,
                        full_digit,
                        prefix_text,
                        suffix_text,
                        style_attr,
                        seq_name,
                    )
                else:
                    # Фоллбек, если цифру почему-то не нашли — выведем просто нативное поле
                    return PandocInjector.text_sequence(
                        raw_link_text,
                        ref_name,
                        seq_name,
                    )

            return f"{tag_open}{raw_link_text}{tag_close}"

        content_str = re.sub(pattern_link, ref_replacer, content_str, flags=re.DOTALL)

        print(f"  [CrossReferenceStrategy]: Закончен. Обернуто ссылок: {count} шт.")
        return content_str
