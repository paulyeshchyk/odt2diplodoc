import re

from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.postProcessing.ODT.CrossReferenceManager import (
    CrossReferenceManager,
)
from diplodoc_converter.intoODT.postProcessing.ODT.PandocInjector import PandocInjector
from diplodoc_converter.intoODT.Transliterator import Transliterator

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

            rough_caption_words = [
                Transliterator.rough_translit(w) for w in significant_words
            ]

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
