# diplodoc_converter/strategies/remove_empty_anchors.py
import re
from .base import TransformationStrategy

class RemoveEmptyAnchorsStrategy(TransformationStrategy):
    def transform(self, content: str) -> str:
        """Удаляет []{#anchor...} только из строк, которые не являются заголовками."""
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            # Если строка начинается с # (заголовок) – оставляем как есть
            if line.strip().startswith('#'):
                new_lines.append(line)
            else:
                # Удаляем []{#anchor-...} и []{#...} из обычного текста
                new_line = re.sub(r'\[\]\{#anchor[^}]*\}', '', line)
                new_line = re.sub(r'\[\]\{[^}]+\}', '', new_line)
                new_lines.append(new_line)
        return '\n'.join(new_lines)