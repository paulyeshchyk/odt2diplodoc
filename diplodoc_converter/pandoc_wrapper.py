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

    extra_args = [
        f"--extract-media={temp_media_dir}",
        # "--filter=fix-sequence-refs",
    ]

    # Добавляем Lua-фильтры с полными путями
    if pandoc_options.lua_options:
        if pandoc_options.lua_options.lua_filter_path:
            for filter_name in pandoc_options.lua_options.lua_filter_path:
                if pandoc_options.lua_options.lua_dir and not Path(filter_name).is_absolute():
                    # Если фильтр из расширения — ищем в lua/
                    full_path = Path(pandoc_options.lua_options.lua_dir) / filter_name
                    if full_path.exists():
                        filter_path = str(full_path)
                    else:
                        filter_path = filter_name
                else:
                    filter_path = filter_name

                extra_args.extend(["--lua-filter", filter_path])
                print(f"2Применяется Lua-фильтр: {filter_path}")

    try:
        pypandoc.convert_file(
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