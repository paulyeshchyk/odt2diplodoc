# diplodoc_converter/image_processor.py

import re
import shutil
from pathlib import Path
from typing import Tuple

from diplodoc_converter.fromODT.utils.os_file_utils import Os_File_Utils


def extract_and_replace_images(
    text: str,
    source_media_dir: Path,
    target_images_dir: Path,
) -> Tuple[str, int]:
    """
    Копирует изображения из временной папки pandoc в папку images каждой секции
    и заменяет ссылки в тексте на относительные (images/имя_файла).
    Сохраняет оригинальный альтернативный текст, удаляя экранирование скобок.
    Возвращает (новый_текст, количество_обработанных_изображений).
    """
    # Паттерн для Markdown-изображений с группами: (альт.текст) и (путь)
    pattern = re.compile(
        r"!\[(.*?)\]\((.*?\.(?:png|jpg|jpeg|gif|svg|bmp))\)", re.IGNORECASE | re.DOTALL
    )

    Os_File_Utils.ensure_dir(target_images_dir)
    count = 0

    def replace_path(match):
        nonlocal count
        alt_text = match.group(1).strip()
        full_src = match.group(2).strip()

        # Очищаем alt-текст от экранирования скобок
        alt_text = alt_text.replace(r"\[", "[").replace(r"\]", "]")
        # Удаляем лишние символы переноса строк, которые могли попасть
        alt_text = re.sub(r"\s+", " ", alt_text).strip()

        # Извлекаем имя файла
        src_path = Path(full_src)
        img_name = src_path.name
        if not img_name:
            return match.group(0)

        # Ищем исходный файл
        source_file = None
        candidates = [
            source_media_dir / img_name,
            source_media_dir / "media" / img_name,
            source_media_dir / "Pictures" / img_name,
            source_media_dir / "Attachments" / img_name,
            Path(full_src),
        ]
        for cand in candidates:
            if cand.exists() and cand.is_file():
                source_file = cand
                break

        if source_file:
            dest_file = target_images_dir / img_name
            if not dest_file.exists():
                shutil.copy2(source_file, dest_file)
            count += 1
            # Собираем новую Markdown-ссылку с очищенным alt-текстом
            return f"![{alt_text}](media/{img_name})"
        else:
            print(
                f"Предупреждение: изображение {full_src} не найдено в {source_media_dir}"
            )
            return match.group(0)

    new_text = pattern.sub(replace_path, text)
    return new_text, count
