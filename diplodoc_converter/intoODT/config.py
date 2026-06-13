# ------------------------------------------------------------
# Конфигурация
# ------------------------------------------------------------
from pathlib import Path


class MdToOdtConfig:
    """Глобальные настройки скрипта сборки ODT из MD."""

    # Расширения изображений, которые копируем
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".bmp", ".tiff"}
    # Ширина в пикселях, после которой картинка масштабируется на 100% ширины страницы
    WIDTH_THRESHOLD = 700
    # Максимальный уровень заголовка Markdown (превышающие урезаются)
    MAX_HEADING_LEVEL = 6
    # Папка с документацией относительно корня скрипта (можно переопределить)
    DEFAULT_INPUT_DIR = "D:/projects/private/gs10_odt/docs/ru"
    # Выходной ODT-файл (можно переопределить)
    DEFAULT_OUTPUT_FILE = "D:/projects/private/gs10_odt/output.odt"
    # Путь к ODT-файлу с пользовательскими стилями (или None)
    REFERENCE_ODT = "D:/projects/private/gs10_odt/reference.odt"
    # Расположение подписи к картинке: под картинкой в виде текста, или внутри в виде названия
    CAPTION_POSITION: str = "inside"  # "below" или "inside"

    # Настройки подписи (только для режима inside)
    CAPTION_STYLE_NAME: str = "Figure"
    CAPTION_PREFIX_TEXT: str = "Рисунок"  # слово перед номером
    CAPTION_SEQUENCE_NAME: str = "Figure"  # имя последовательности (text:name)
    CAPTION_FORMULA: str = "ooow:Figure+1"  # формула нумерации

    @classmethod
    def normalize_rel_path(cls, rel_path: Path) -> Path:
        """Удаляет пустые компоненты из относительного пути."""
        clean_parts = [p for p in rel_path.parts if p and p != "."]
        return Path(*clean_parts)

    @classmethod
    def update(cls, **kwargs):
        """Обновляет настройки класса переданными значениями."""
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
