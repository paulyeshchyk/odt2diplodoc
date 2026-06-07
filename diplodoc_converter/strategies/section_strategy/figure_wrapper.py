# diplodoc_converter/section_strategy/figure_wrapper.py
import re
from diplodoc_converter.section_parser import Section
from diplodoc_converter.strategies.section_strategy.base import SectionStrategy
        
class WrapImagesInFiguresStrategy(SectionStrategy):
    def transform_section(self, sec: Section) -> None:
        sec.body = self._transform_body(sec.body)   # старый метод transform переименован
        
    def _transform_body(self, content: str) -> str:
        # Паттерн для поиска изображения с возможным атрибутом
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
            # Возвращаем Markdown-изображение и подпись курсивом
            return f"![{full_alt}]({src})\n\n*{full_alt}*\n\n"
        
        # Заменяем изображения с подписями
        new_content = pattern.sub(repl, content)
        
        # # Удаляем оставшиеся {alt=...} (более простой способ)
        # # Ищем любую конструкцию {alt="..."} или {alt='...'} и удаляем её
        # new_content = re.sub(r'\{alt=["\'][^"\']*["\']\}', '', new_content)
        
        return new_content