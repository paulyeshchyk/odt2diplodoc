import re
from typing import List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Section:
    title: str
    level: int          # 1 для H1, 2 для H2...
    body: str
    children: List['Section']
    slug: str = ""
    relative_path: Path | None = None

def parse_sections(markdown_content: str) -> List[Section]:
    """Разбирает Markdown на вложенные секции по заголовкам # ## ###."""
    lines = markdown_content.splitlines()
    sections = []
    stack = []
    current_section = None
    current_body_lines = []
    heading_re = re.compile(r'^(#{1,6})\s+(.*)$')
    
    def flush():
        nonlocal current_section, current_body_lines
        if current_section is not None:
            current_section.body = '\n'.join(current_body_lines).strip()
            while stack and stack[-1].level >= current_section.level:
                stack.pop()
            if stack:
                stack[-1].children.append(current_section)
            else:
                sections.append(current_section)
            if not stack or current_section.level < stack[-1].level:
                stack.append(current_section)
        current_section = None
        current_body_lines = []
    
    print("Разбор структуры документа...")
    for line in lines:
        match = heading_re.match(line)
        if match:
            flush()
            level = len(match.group(1))
            title = match.group(2).strip()
            current_section = Section(title=title, level=level, body="", children=[])
        else:
            if current_section is not None:
                current_body_lines.append(line)
    flush()
    return sections

def flatten_sections(sections: List[Section]) -> List[Section]:
    """Разворачивает дерево в плоский список (порядок обхода в глубину)."""
    result = []
    def dfs(sec):
        result.append(sec)
        for child in sec.children:
            dfs(child)
    for sec in sections:
        dfs(sec)
    return result