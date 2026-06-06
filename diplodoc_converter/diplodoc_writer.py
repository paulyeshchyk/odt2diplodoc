from pathlib import Path
import yaml
from typing import List
from .utils import ensure_dir
from .section_parser import Section

def write_section_tree(sections: List[Section], output_dir: Path, root_title: str = "Документация") -> None:
    """Создаёт папки, index.md, index.yaml, toc.yaml для всех секций."""
    # Сначала обработаем всех детей рекурсивно, но проще вызвать _write_section для корневых
    root_items = []
    for sec in sections:
        sec_path = output_dir / sec.slug
        _write_section(sec, sec_path, output_dir)
        root_items.append({
            "name": sec.title,
            "href": f"{sec.slug}/toc.yaml"
        })
    
    root_toc = {"title": root_title, "items": root_items}
    with open(output_dir / "toc.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(root_toc, f, allow_unicode=True, sort_keys=False)

def _write_section(sec: Section, folder_path: Path, root_output_dir: Path) -> None:
    ensure_dir(folder_path)
    
    # index.md
    (folder_path / "index.md").write_text(sec.body, encoding='utf-8')
    
    # index.yaml
    index_yaml = {"title": sec.title, "meta": {"title": sec.title}}
    with open(folder_path / "index.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(index_yaml, f, allow_unicode=True, sort_keys=False)
    
    # Рекурсивно обработать детей
    toc_items = []
    for child in sec.children:
        child_path = folder_path / child.slug
        _write_section(child, child_path, root_output_dir)
        toc_items.append({
            "name": child.title,
            "href": f"{child.slug}/toc.yaml"
        })
    
    own_item = {"name": sec.title, "href": "index.md"}
    toc_yaml = {"title": sec.title, "items": [own_item] + toc_items}
    with open(folder_path / "toc.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(toc_yaml, f, allow_unicode=True, sort_keys=False)