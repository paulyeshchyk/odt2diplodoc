# diplodoc_converter/pandoc_wrapper.py
from dataclasses import dataclass
from pathlib import Path
from .config import PandocOptions


@dataclass
class PandocContext:
    odt_path: Path
    temp_md_path: Path
    temp_media_dir: Path


@dataclass
class PyPandocContext:
    source_file: str
    pandoc_fmt: str
    output_fmt: str
    extra_args: list[str]
    outputfile: str


class PyPandocContextBuilder:
    def insert_lua_filters(
        self,
        extra_args: list[str],
        original_cwd: Path,
        pandoc_options: PandocOptions,
    ):
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

    def build(
        self,
        original_cwd: Path,
        pandoc_ctx: PandocContext,
        pandoc_options: PandocOptions,
    ):
        fmt = pandoc_options.to_pandoc_string()
        print(f"Формат Pandoc: -t {fmt}")

        extra_args = ["--extract-media=media"]
        extra_args.append("--wrap=none")

        self.insert_lua_filters(extra_args, original_cwd, pandoc_options)

        source_file = Path(pandoc_ctx.odt_path)
        if not source_file.is_absolute():
            source_file = original_cwd / source_file
        return PyPandocContext(
            str(source_file),
            fmt,
            "odt",
            extra_args,
            pandoc_ctx.temp_md_path.name,
        )
