# diplodoc_converter/diplodoc_writer.py

from pathlib import Path
import yaml
from typing import List
from .utils import ensure_dir
from .section_parser import Section

def write_section_tree(sections: List[Section], output_dir: Path, root_title: str = "Документация") -> None:
    # Корневые файлы
    root_index_content = render_index_md(root_title, "Section", "")
    (output_dir / "index.md").write_text(root_index_content, encoding='utf-8')
    
    root_index_yaml = {
        "title": root_title,
        "href": "index.md",
        "meta": {"title": root_title}
    }
    with open(output_dir / "index.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(root_index_yaml, f, allow_unicode=True, sort_keys=False, indent=2)
    
    # Рекурсивно создаём все секции
    for sec in sections:
        _write_section(sec, output_dir)
    
    # Корневой toc.yaml
    root_items = []
    for sec in sections:
        root_items.append({
            "name": sec.title,
            "href": f"{sec.slug}/index.md",
            "include": {
                "path": f"{sec.slug}/toc.yaml",
                "mode": "link"
            }
        })
    root_toc = {
        "title": root_title,
        "href": "index.yaml",
        "items": root_items
    }
    with open(output_dir / "toc.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(root_toc, f, allow_unicode=True, sort_keys=False, indent=2)

def render_index_md(title: str, section_type: str, body: str) -> str:
    frontmatter = f"""---
title: {title}
sectionType: {section_type}
pureTitle: {title}
---
"""
    return frontmatter + ("\n" + body if body.strip() else "")

def _write_section(sec: Section, output_root: Path) -> None:
    """Создаёт файлы для одной секции по её full_slug. Рекурсивно вызывает для детей."""

    if sec.full_slug is None:
        raise RuntimeError(f"full_slug не установлен для секции '{sec.title}'")
    folder_path = output_root / sec.full_slug
    ensure_dir(folder_path)
    
    section_type = "Section" if sec.level == 1 else "Chapter"
    md_content = render_index_md(sec.title, section_type, sec.body)
    (folder_path / "index.md").write_text(md_content, encoding='utf-8')
    
    index_yaml = {
        "title": sec.title,
        "href": "index.md",
        "meta": {"title": sec.title}
    }
    with open(folder_path / "index.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(index_yaml, f, allow_unicode=True, sort_keys=False, indent=2)
    
    # Рекурсивно обрабатываем детей
    toc_items = []
    for child in sec.children:
        _write_section(child, output_root)
        toc_items.append({
            "name": child.title,
            "href": f"{child.slug}/index.md",
            "include": {
                "path": f"{child.slug}/toc.yaml",
                "mode": "link"
            }
        })
    
    toc_yaml = {
        "title": sec.title,
        "href": "index.yaml",
        "items": toc_items
    }
    with open(folder_path / "toc.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(toc_yaml, f, allow_unicode=True, sort_keys=False, indent=2)