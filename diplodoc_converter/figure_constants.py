# diplodoc_converter/figure_constants.py
# Настройки для работы с подписями и перекрёстными ссылками на рисунки

# --- Язык и стиль ---
FIGURE_PREFIX = "рис."                # префикс в тексте ссылки (например, "(рис. 2)")
FIGURE_CAPTION_PREFIX = "Рисунок"     # слово перед номером в подписи
FIGURE_MARKER = "fig"                 # идентификатор в метке {#fig:N}
CAPTION_SEPARATOR = ". "              # разделитель между номером и текстом подписи

# --- Пути и папки ---
SOURCE_IMAGE_FOLDER = "Pictures/"     # папка внутри ODT, куда Pandoc кладёт извлечённые изображения
TARGET_IMAGE_FOLDER = "media/"        # целевая папка относительно index.md

# --- Регулярные выражения (можно оставить как строки) ---
REFERENCE_PATTERN = r'\(рис\.\s*(\d+)\)'        # ссылка с номером
PLACEHOLDER_PATTERN = r'\(рис\.\s*\)'           # пустая ссылка (без номера)