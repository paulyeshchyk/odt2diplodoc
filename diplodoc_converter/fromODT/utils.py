#!/usr/bin/env python3
# diplodoc_converter/utils.py

import re
from pathlib import Path


def slugify(text: str, max_length: int = 50) -> str:
    """Превращает заголовок в безопасное имя для папки/файла."""
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[-\s]+", "_", s).strip("-_")
    return s[:max_length]


def ensure_dir(path: Path) -> None:
    """Создаёт директорию, если её нет."""
    path.mkdir(parents=True, exist_ok=True)


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: Path, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_folder_name(title: str) -> str:
    """
    Генерирует имя папки из заголовка для Windows:
    - Регистр сохраняется.
    - Пробелы удаляются.
    - Допустимые символы: буквы (включая кириллицу), цифры, точка, подчёркивание.
    - Дефис и другие символы удаляются.
    """
    # Удаляем пробелы
    result = re.sub(r"\s+", "", title)
    # Оставляем только буквы, цифры, точку, подчёркивание (дефис и прочее удаляем)
    result = re.sub(r"[^\w\.]", "", result, flags=re.UNICODE)
    # Убираем возможные лишние точки в конце
    result = result.rstrip(".")
    if not result:
        result = "Bez_nazvaniya"
    return result
