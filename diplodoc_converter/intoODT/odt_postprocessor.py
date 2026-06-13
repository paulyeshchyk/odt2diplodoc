import os
import re
import zipfile
from pathlib import Path
from diplodoc_converter.intoODT.config import MdToOdtConfig

# ------------------------------------------------------------
# Постобработка ODT
# ------------------------------------------------------------


class OdtPostProcessor:
    def __init__(self, odt_path: Path):
        self.odt_path = odt_path

    def run(self, strategies):
        print("[ODT постобработка]: Начат")
        temp_odt = self.odt_path.with_suffix(".tmp.odt")
        modified = False

        with (
            zipfile.ZipFile(self.odt_path, "r") as yin,
            zipfile.ZipFile(temp_odt, "w", zipfile.ZIP_DEFLATED) as yout,
        ):
            for item in yin.infolist():
                content = yin.read(item.filename)
                if item.filename == "content.xml":
                    content_str = content.decode("utf-8")
                    original = content_str

                    # ВАЖНО: Передаем управление стратегиям.
                    # Чтобы они могли общаться, мы можем выполнять их последовательно.
                    for strat in strategies:
                        content_str = strat.process(content_str)

                    if content_str != original:
                        modified = True
                    content = content_str.encode("utf-8")
                yout.writestr(item, content)

        if modified:
            os.remove(self.odt_path)
            os.rename(temp_odt, self.odt_path)
            print(
                f"[ODT постобработка]: Закончен. Применено стратегий: {len(strategies)}"
            )
        else:
            os.remove(temp_odt)
            print("[ODT постобработка]: Изменений не потребовалось")


class CrossReferenceManager:
    """
    Глобальный менеджер для Фазы 2. Связывает
    Pandoc-ссылки с нативными последовательностями LibreOffice.
    """

    # Карта: "полный_id_из_ссылки_pandoc" -> "уникальный_ref_name_для_ODT"
    id_to_ref_map = {}

    # Список всех обнаруженных в документе полных ID из тегов <text:a>
    detected_pandoc_ids = []

    @classmethod
    def extract_all_links(cls, content_str: str):
        """
        Ищет все ссылки, содержащие 'fig-'.
        Захватывает ID целиком, включая префиксы документов.
        """
        cls.detected_pandoc_ids = re.findall(
            r'xlink:href="#([^"]*fig-[^"]+)"', content_str
        )


# ------------------------------------------------------------
# Стратегия 1: Поиск маркеров картинок и врезка TextBox
# ------------------------------------------------------------


class FigureCaptionStrategy:
    def process(self, content_str: str) -> str:
        if MdToOdtConfig.CAPTION_POSITION != "inside":
            return content_str

        print("[FigureCaptionStrategy]: Начат")

        # Шаг 1. Собираем все реальные ссылки из документа
        CrossReferenceManager.extract_all_links(content_str)
        CrossReferenceManager.id_to_ref_map.clear()

        # Локальный счетчик только для draw:name="Рисунок_X" (визуальное имя фрейма)
        display_counter = 0

        style_name = MdToOdtConfig.CAPTION_STYLE_NAME
        prefix = MdToOdtConfig.CAPTION_PREFIX_TEXT
        seq_name = MdToOdtConfig.CAPTION_SEQUENCE_NAME
        formula = MdToOdtConfig.CAPTION_FORMULA

        def find_best_matching_pandoc_id(caption_text: str) -> str | None:
            """
            Ищет среди собранных Pandoc ID тот, который содержит транслит слов подписи.
            """
            words = re.findall(r"[а-яa-z0-9]+", caption_text.lower())
            significant_words = [w[:4] for w in words if len(w) > 2]

            if not significant_words:
                return None

            def rough_translit(text: str) -> str:
                trans = {
                    "щ": "shch",
                    "ш": "sh",
                    "ч": "ch",
                    "ж": "zh",
                    "х": "h",
                    "ц": "c",
                    "ю": "yu",
                    "я": "ya",
                    "а": "a",
                    "б": "b",
                    "в": "v",
                    "г": "g",
                    "д": "d",
                    "е": "e",
                    "ё": "e",
                    "з": "z",
                    "и": "i",
                    "й": "j",
                    "к": "k",
                    "л": "l",
                    "м": "m",
                    "н": "n",
                    "о": "o",
                    "п": "p",
                    "р": "r",
                    "с": "s",
                    "т": "t",
                    "у": "u",
                    "ф": "f",
                    "ы": "y",
                    "э": "e",
                }
                return "".join([trans.get(c, c) for c in text])

            rough_caption_words = [rough_translit(w) for w in significant_words]

            best_id = None
            max_matches = 0

            for p_id in CrossReferenceManager.detected_pandoc_ids:
                matches = sum(1 for w in rough_caption_words if w in p_id.lower())
                if matches > max_matches:
                    max_matches = matches
                    best_id = p_id

            return best_id

        def replacer(match):
            nonlocal display_counter
            frame_block = match.group(1)
            raw_caption = match.group(2).strip()

            caption_text = re.sub(r"<[^>]+>", "", raw_caption).strip()

            # Извлечение размеров
            width_match = re.search(r'svg:width="([^"]+)"', frame_block)
            height_match = re.search(r'svg:height="([^"]+)"', frame_block)
            w_str = width_match.group(1) if width_match else "17cm"
            h_str = height_match.group(1) if height_match else "10cm"

            outer_h_str = h_str
            if "pt" in h_str:
                try:
                    h_val = float(h_str.replace("pt", ""))
                    outer_h_str = f"{h_val + 32.0}pt"
                except ValueError:
                    pass

            image_match = re.search(r"(<draw:image[^>]+>)", frame_block)
            image_tag = image_match.group(1) if image_match else ""
            if not image_tag:
                return frame_block

            display_counter += 1
            safe_caption = caption_text.replace('"', "&quot;")

            # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Формируем ref_name на основе ID самого Pandoc ---
            matched_pandoc_id = find_best_matching_pandoc_id(caption_text)

            if matched_pandoc_id:
                # Очищаем ID от лишних символов (оставляем только буквы, цифры и подчеркивания для корректности ODT)
                clean_suffix = re.sub(r"[^a-zA-Z0-9_]", "_", matched_pandoc_id)
                ref_name = f"ref_{clean_suffix}"
                # Запоминаем связь: полный Pandoc ID -> наш чистый ref_name
                CrossReferenceManager.id_to_ref_map[matched_pandoc_id] = ref_name
            else:
                # На случай, если на картинку никто не сослался в тексте, делаем фоллбек
                ref_name = f"refFigureFallback_{display_counter}"

            return PandocInjector.draw_frame(
                caption_text=caption_text,
                w_str=w_str,
                h_str=h_str,
                outer_h_str=outer_h_str,
                image_tag=image_tag,
                safe_caption=safe_caption,
                ref_name=ref_name,
                prefix=prefix,
                display_counter=display_counter,
                style_name=style_name,
                formula=formula,
                seq_name=seq_name,
            )

        pattern = r"(<draw:frame[^>]+>.*?</draw:frame>).*?%%%CAPTION_START%%%(.*?)%%%CAPTION_END%%%(?:.*?\|\|\|ID:[^|]+\|\|\|)?"
        new_content = re.sub(pattern, replacer, content_str, flags=re.DOTALL)
        new_content = re.sub(
            r'<text:p text:style-name="[^"]+">\s*</text:p>', "", new_content
        )

        print(
            f"[FigureCaptionStrategy]: Закончен. Обработано иллюстраций: {display_counter}"
        )
        return new_content


# ------------------------------------------------------------
# Стратегия 2: Замена ссылок Pandoc на ссылки LibreOffice
# ------------------------------------------------------------


class CrossReferenceStrategy:
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

        print(
            f"  [CrossReferenceStrategy]: Закончен. Красиво обернуто ссылок: {count} шт."
        )
        return content_str


class PandocInjector:
    @staticmethod
    def text_sequence(raw_link_text, ref_name, seq_name):
        return (
            f'<text:sequence-ref text:reference-format="value" '
            f'text:sequence-name="{seq_name}" text:ref-name="{ref_name}">'
            f"{raw_link_text}"
            f"</text:sequence-ref>"
        )

    @staticmethod
    def text_sequence_suffix(
        ref_name, full_digit, prefix_text, suffix_text, style_attr, seq_name
    ):
        return (
            f"<text:span{style_attr}>"
            f"{prefix_text}"
            f'<text:sequence-ref text:reference-format="value" '
            f'text:sequence-name="{seq_name}" text:ref-name="{ref_name}">'
            f"{full_digit}"
            f"</text:sequence-ref>"
            f"{suffix_text}"
            f"</text:span>"
        )

    @staticmethod
    def draw_frame(
        caption_text,
        w_str,
        h_str,
        outer_h_str,
        image_tag,
        safe_caption,
        ref_name,
        prefix,
        display_counter,
        style_name,
        formula,
        seq_name,
    ):
        return (
            f'<draw:frame draw:style-name="Graphics" draw:name="{prefix}_{display_counter}" '
            f'text:anchor-type="paragraph" svg:width="{w_str}" style:rel-width="100%" '
            f'svg:height="{outer_h_str}" style:rel-height="scale-min" draw:z-index="{display_counter}">'
            f"<draw:text-box>"
            f'<text:p text:style-name="{style_name}">'
            f'<draw:frame draw:name="Graphic_{safe_caption}" svg:title="{safe_caption}" '
            f'text:anchor-type="paragraph" svg:width="{w_str}" style:rel-width="100%" '
            f'svg:height="{h_str}" style:rel-height="scale" draw:z-index="1">'
            f"{image_tag}"
            f"</draw:frame>"
            f'{prefix} <text:sequence text:ref-name="{ref_name}" text:name="{seq_name}" '
            f'text:formula="{formula}" style:num-format="1">{display_counter}</text:sequence>: {caption_text}'
            f"</text:p>"
            f"</draw:text-box>"
            f"</draw:frame>"
        )
