import tempfile
import zipfile
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


def process_odt_with_delegate(odt_path: Path, delegate: Callable[[Path], T]) -> T:
    """
    Распаковывает ODT-файл во временную папку, вызывает делегат для внесения
    изменений, затем запаковывает изменённые файлы обратно в ODT.

    :param odt_path: Путь к исходному ODT-файлу (будет перезаписан!)
    :param delegate: Функция, принимающая путь к временной папке с распакованным
                     ODT и возвращающая любой результат (например, словарь).
    :return: Результат, возвращённый делегатом.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # 1. Распаковка
        with zipfile.ZipFile(odt_path, "r") as zf:
            zf.extractall(tmp_path)

        # 2. Вызов делегата – здесь делаются все изменения
        result = delegate(tmp_path)

        # 3. Запаковка обратно (перезаписывает исходный файл)
        with zipfile.ZipFile(odt_path, "w") as zf:
            for file_path in tmp_path.rglob("*"):
                zf.write(file_path, arcname=file_path.relative_to(tmp_path))

        return result
