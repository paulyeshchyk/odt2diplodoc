# diplodoc_converter/pandoc_wrapper.py
# diplodoc_converter/pandoc_wrapper.py

import pypandoc
from pathlib import Path
from .utils import ensure_dir
from .config import PandocOptions


def convert_odt_to_markdown(
    odt_path: Path, 
    temp_md_path: Path, 
    temp_media_dir: Path, 
    pandoc_options: PandocOptions
) -> str:
    ensure_dir(temp_media_dir)

    fmt = pandoc_options.to_pandoc_string()
    print(f"Формат Pandoc: -t {fmt}")

    # Дополнительные аргументы
    extra_args = [
        f"--extract-media={temp_media_dir}",
        "--filter=pandoc-crossref",
    ]

    # Добавляем Lua-фильтры
    if pandoc_options.lua_filter_path:
        for lua_filter in pandoc_options.lua_filter_path:
            extra_args.extend(["--lua-filter", lua_filter])
            print(f"Применяется Lua-фильтр: {lua_filter}")

    try:
        output = pypandoc.convert_file(
            source_file=str(odt_path),
            to=fmt,
            format='odt',
            extra_args=extra_args,
            outputfile=str(temp_md_path)
        )
        print("Конвертация через pypandoc прошла успешно.")
    except Exception as e:
        raise RuntimeError(f"Ошибка pypandoc: {e}") from e

    return temp_md_path.read_text(encoding="utf-8")