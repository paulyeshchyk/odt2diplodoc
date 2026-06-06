import re
from pathlib import Path
from typing import Dict, List
from .utils import slugify
from .section_parser import Section, flatten_sections

def normalize_title(title: str) -> str:
    """Приводит заголовок к виду для якорей (#zagolovok-s-defisami)."""
    s = re.sub(r'[^\w\s-]', '', title.lower())
    s = re.sub(r'[-\s]+', '-', s).strip('-')
    return s

def build_slug_map(sections: List[Section], base_output_dir: Path) -> Dict[str, Path]:
    """Создаёт словарь: нормализованный заголовок -> путь к index.md."""
    slug_map = {}
    # Сначала убедимся, что у всех секций есть slug
    slug_counter = {}
    def assign_slug(sec):
        slug = slugify(sec.title)
        if slug in slug_counter:
            slug_counter[slug] += 1
            slug = f"{slug}_{slug_counter[slug]}"
        else:
            slug_counter[slug] = 1
        sec.slug = slug
        for child in sec.children:
            assign_slug(child)
    for sec in sections:
        assign_slug(sec)
    
    # Теперь маппинг
    for sec in flatten_sections(sections):
        norm = normalize_title(sec.title)
        rel_path = Path(sec.slug) / "index.md"
        slug_map[norm] = rel_path
        slug_map[sec.slug] = rel_path   # прямой slug тоже
    return slug_map

def replace_internal_links(text: str, slug_map: Dict[str, Path], current_section_slug: str) -> str:
    """Заменяет внутренние ссылки вида [текст](#заголовок) на пути к другим статьям."""
    def repl(match):
        full_match = match.group(0)
        link_text = match.group(1)
        target = match.group(2)
        if target.endswith('.md'):
            target = target[:-3]
        if target.startswith('#'):
            target = target[1:]
        target_norm = normalize_title(target)
        if target_norm in slug_map:
            target_path = slug_map[target_norm]
            # Строим абсолютный от корня документации (для Diplodoc)
            return f"[{link_text}](/{target_path.as_posix()})"
        else:
            return full_match  # не трогаем
    
    pattern = r'\[([^\]]+)\]\((?!https?://|mailto:)([^)]+)\)'
    return re.sub(pattern, repl, text)