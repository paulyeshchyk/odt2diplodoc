import re
from pathlib import Path
from .base import TransformationStrategy

class WrapImagesInFiguresStrategy(TransformationStrategy):
    def transform(self, content: str) -> str:
        pattern = re.compile(
            r'!\[(.*?)\]\((images|media)/([^)]+)\)\s*(\{alt=("|\')(.*?)\5\})?',
            re.DOTALL
        )

        def repl(m):
            short_alt = m.group(1).strip()
            folder = m.group(2)
            filename = m.group(3)
            full_alt = m.group(6) if m.group(6) else short_alt
            # Очистка экранирования
            full_alt = full_alt.replace(r'\"', '"').replace(r"\&quot;", '"')
            full_alt = re.sub(r'\\([\[\]])', r'\1', full_alt)
            
            # Добавляем пробел после "Рисунок 12." если его нет
            full_alt = re.sub(r'(Рисунок\s+\d+\.)(\S)', r'\1 \2', full_alt)
            src = f"{folder}/{filename}"
            return f"![{full_alt}]({src})\n\n*{full_alt}*\n\n"
        
        new_content = pattern.sub(repl, content)
        new_content = re.sub(r'\s*\{alt=("|\')(?:[^\\]|\\.)*?\1\}', '', new_content, flags=re.DOTALL)
        return new_content