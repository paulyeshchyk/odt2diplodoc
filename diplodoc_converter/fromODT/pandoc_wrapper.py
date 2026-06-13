# diplodoc_converter/pandoc_wrapper.py
import os
import pypandoc
from pathlib import Path
from .utils import ensure_dir
from .config import PandocOptions


def convert_odt_to_markdown(
    odt_path: Path,
    temp_md_path: Path,
    temp_media_dir: Path,
    pandoc_options: PandocOptions,
) -> str:
    ensure_dir(temp_media_dir)
    fmt = pandoc_options.to_pandoc_string()
    print(f"Формат Pandoc: -t {fmt}")

    original_cwd = Path.cwd()
    target_dir = temp_media_dir.parent
    os.chdir(target_dir)
    try:
        extra_args = ["--extract-media=media"]
        extra_args.append(f"--wrap=none")

        # Lua-фильтры
        if pandoc_options.lua_options and pandoc_options.lua_options.lua_filter_path:
            lua_dir = None
            if pandoc_options.lua_options.lua_dir:
                lua_dir = Path(pandoc_options.lua_options.lua_dir)
                if not lua_dir.is_absolute():
                    lua_dir = original_cwd / lua_dir

            for filter_name in pandoc_options.lua_options.lua_filter_path:
                if filter_name == "logging.lua":
                    continue
                filter_path = Path(filter_name)
                if not filter_path.is_absolute():
                    if lua_dir and (lua_dir / filter_name).exists():
                        filter_path = lua_dir / filter_name
                    else:
                        filter_path = original_cwd / filter_name
                if filter_path.exists():
                    extra_args.extend(["--lua-filter", str(filter_path)])
                else:
                    print(f"Предупреждение: Lua-фильтр не найден: {filter_path}")

        source_file = Path(odt_path)
        if not source_file.is_absolute():
            source_file = original_cwd / source_file

        pypandoc.convert_file(
            source_file=str(source_file),
            to=fmt,
            format="odt",
            extra_args=extra_args,
            outputfile=temp_md_path.name,
        )
        result = temp_md_path.read_text(encoding="utf-8")
    finally:
        os.chdir(original_cwd)
    return result
