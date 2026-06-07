# diplodoc_converter/section_parser.py

import re
from typing import List
from dataclasses import dataclass
from pathlib import Path
from .config import ParserSettings

@dataclass
class Section:
    title: str
    level: int
    body: str
    children: List['Section']
    slug: str = ""            # короткое имя папки
    full_slug: Path | None = None    # полный путь от корня
    relative_path: Path | None = None
    anchor: str | None = None

def parse_sections(markdown_content: str, parser_settings: ParserSettings | None = None) -> List[Section]:
    if parser_settings is None:
        parser_settings = ParserSettings()
    
    max_level = parser_settings.max_heading_level_for_single_page
    if max_level < 1 or max_level > 6:
        raise ValueError("max_heading_level_for_single_page должно быть от 1 до 6")
    
    lines = markdown_content.splitlines()
    root_sections: List[Section] = []
    stack: List[Section] = []
    current_section: Section | None = None
    current_body_lines: List[str] = []
    
    heading_re = re.compile(r'^(#{1,6})\s+(.*)$')
    
    def clean_heading(raw: str) -> str:
        """Очищает заголовок от мусора Pandoc, но оставляет якорь для отдельного извлечения."""
        # Удаляем HTML-теги
        s = re.sub(r'<[^>]+>', '', raw)
        # Удаляем конструкции [текст]{#anchor} и []{#anchor}
        s = re.sub(r'\[[^\]]*\]\{#[^}]+\}', '', s)
        # Удаляем оставшиеся [] и {}
        s = re.sub(r'\[\]|\{\}', '', s)
        # Удаляем голые слова anchor-123
        s = re.sub(r'\banchor[-_][0-9]+\b', '', s)
        # Убираем лишние пробелы
        s = re.sub(r'\s+', ' ', s).strip()
        return s
    
    def extract_anchor(raw: str) -> str | None:
        """Извлекает якорь вида anchor-123 из конструкции []{#anchor-123}."""
        match = re.search(r'\[\]\{#(anchor-\d+)\}', raw)
        return match.group(1) if match else None
    
    def flush():
        nonlocal current_section, current_body_lines
        if current_section is not None:
            current_section.body = '\n'.join(current_body_lines).strip()
            while stack and stack[-1].level >= current_section.level:
                stack.pop()
            if stack:
                stack[-1].children.append(current_section)
            else:
                root_sections.append(current_section)
            stack.append(current_section)
            current_section = None
            current_body_lines = []
    
    for line in lines:
        match = heading_re.match(line)
        if match:
            level = len(match.group(1))
            raw_title = match.group(2).strip()
            
            # Извлекаем якорь ДО очистки
            anchor = extract_anchor(raw_title)
            cleaned = clean_heading(raw_title)
            if anchor:
                print(f"Найден якорь {anchor} для заголовка '{cleaned}'")            
            
            if not cleaned:
                if current_section is not None:
                    current_body_lines.append(line)
                continue
            
            if level <= max_level:
                flush()
                current_section = Section(
                    title=cleaned,
                    level=level,
                    body="",
                    children=[],
                    anchor=anchor
                )
            else:
                if current_section is not None:
                    current_body_lines.append(line)
        else:
            if current_section is not None:
                current_body_lines.append(line)
    
    flush()
    return root_sections

def flatten_sections(sections: List[Section]) -> List[Section]:
    result = []
    def dfs(sec: Section):
        result.append(sec)
        for child in sec.children:
            dfs(child)
    for sec in sections:
        dfs(sec)
    return result