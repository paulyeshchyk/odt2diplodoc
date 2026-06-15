import re

from diplodoc_converter.intoODT.preprocessing.MD.ProcessingContext import (
    ProcessingContext,
)


class BulletListNormalizer:
    @staticmethod
    def process(ctx: ProcessingContext) -> None:
        ctx.content = BulletListNormalizer.normalize_bullet_lists(ctx.content)

    @staticmethod
    def normalize_bullet_lists(content: str) -> str:
        """
        Заменяет маркеры списков '+' на стандартные '-',
        а также обеспечивает пустую строку перед списком, чтобы предотвратить слипание.
        """
        # Шаг 1: Заменяем '+' на '-' только в начале строк (учитывая пробелы перед ними)
        # re.MULTILINE обязателен
        content = re.sub(r"^(\s*)\+\s+", r"\1- ", content, flags=re.MULTILINE)

        # Шаг 2: Исправляем слипание с предыдущим текстом.
        # Ищем ситуацию, когда идет строка с текстом (не заголовок и не пустая),
        # а на следующей строке сразу начинается список '- '.
        # Добавляем между ними правильный перенос строки.
        def list_spacing_replacer(match):
            prev_line = match.group(1)
            list_line = match.group(2)
            # Если предыдущая строка уже пустая или это заголовок/блок кода, не трогаем
            if not prev_line.strip() or prev_line.strip().startswith(
                ("#", "-", "*", "+", "`")
            ):
                return match.group(0)
            return f"{prev_line}\n\n{list_line}"

        # Ищем пару строк: любая строка -> перенос строки -> строка списка
        pattern = r"^([^\n]+)\n(\s*-\s+.*)$"
        return re.sub(pattern, list_spacing_replacer, content, flags=re.MULTILINE)
