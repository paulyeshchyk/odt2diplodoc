# diplodoc_converter/diplodoc_writer.py

import re


def shift_headings(content: str, shift: int, min_level: int = 1) -> str:
    """Сдвигает уровни Markdown-заголовков на shift, не опуская ниже min_level."""

    def repl(m):
        hashes = m.group(1)
        new_level = len(hashes) + shift
        if new_level < min_level:
            new_level = min_level
        return "#" * new_level + m.group(2)

    pattern = r"^(#{1,6})(\s+.*)$"
    return re.sub(pattern, repl, content, flags=re.MULTILINE)
