import re
import shutil
from pathlib import Path
from typing import Tuple
from .utils import ensure_dir

def extract_and_replace_images(
    text: str,
    source_media_dir: Path,
    target_images_dir: Path
) -> Tuple[str, int]:
    """Копирует изображения и заменяет пути в тексте."""
    img_pattern = re.compile(
        r'(?:!\[.*?\]\(|<img\s+[^>]*src=")([^"\)]+\.(?:png|jpg|jpeg|gif|svg|bmp))',
        re.IGNORECASE
    )
    
    ensure_dir(target_images_dir)
    count = 0
    
    def replace_path(match):
        nonlocal count
        full_src = match.group(1)
        source_file = None
        candidates = [
            source_media_dir / full_src,
            source_media_dir / Path(full_src).name,
            source_media_dir / 'media' / Path(full_src).name,
            source_media_dir / 'Pictures' / Path(full_src).name,
        ]
        for cand in candidates:
            if cand.exists():
                source_file = cand
                break
        
        if source_file:
            dest_file = target_images_dir / source_file.name
            shutil.copy2(source_file, dest_file)
            count += 1
            return f"![image](images/{source_file.name})"
        else:
            print(f"Предупреждение: не найдено изображение {full_src}")
            return match.group(0)
    
    new_text = img_pattern.sub(replace_path, text)
    return new_text, count