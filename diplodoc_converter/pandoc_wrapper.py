# diplodoc_converter/pandoc_wrapper.py

import subprocess
import shutil
from pathlib import Path
from .utils import ensure_dir
from .config import PandocOptions

def convert_odt_to_markdown(odt_path: Path, temp_md_path: Path, temp_media_dir: Path, pandoc_options: PandocOptions) -> str:
    if not shutil.which('pandoc'):
        raise RuntimeError("Pandoc не найден. Установите pandoc и добавьте в PATH.")

    ensure_dir(temp_media_dir)

    fmt = pandoc_options.to_pandoc_string()
    print(f"Формат Pandoc: -t {fmt}")

    try:
        subprocess.run([
            'pandoc', str(odt_path),
            '-f', 'odt',
            '-t', fmt,
            '--lua-filter=no-img-size.lua',
            f'--extract-media={temp_media_dir}',
            '-o', str(temp_md_path)
        ], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка pandoc: {e.stderr}") from e

    return temp_md_path.read_text(encoding='utf-8')