import re


class CrossReferenceManager:
    """
    Глобальный менеджер для Фазы 2. Связывает
    Pandoc-ссылки с нативными последовательностями LibreOffice.
    """

    # Карта: "полный_id_из_ссылки_pandoc" -> "уникальный_ref_name_для_ODT"
    id_to_ref_map: dict[str, str] = {}

    # Список всех обнаруженных в документе полных ID из тегов <text:a>
    detected_pandoc_ids: list[str] = []

    @classmethod
    def extract_all_links(cls, content_str: str):
        """
        Ищет все ссылки, содержащие 'fig-'.
        Захватывает ID целиком, включая префиксы документов.
        """
        cls.detected_pandoc_ids = re.findall(
            r'xlink:href="#([^"]*fig-[^"]+)"', content_str
        )
