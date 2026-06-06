# diplodoc_converter/strategies/remove_pandoc_attrs.py
import re
from .base import TransformationStrategy

class RemovePandocAttributesStrategy(TransformationStrategy):
    def transform(self, content: str) -> str:
        # Удаляет {alt="..."} и {alt='...'} с учётом экранированных кавычек внутри
        pattern = r'\{alt=("|\')(?:[^\\]|\\.)*?\1\}'
        # multi-line не обязателен, так как точечный шаблон с \n работает
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        # Удаляем возможные пустые строки
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content