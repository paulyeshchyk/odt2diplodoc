# diplodoc_converter/section_strategy/two_column_table_note_strategy.py
import re

from diplodoc_converter.fromODT.md.strategies.section.MDSectionStrategy import (
    MDSectionStrategy,
)
from diplodoc_converter.fromODT.model.Section import Section


class MDSectionStrategyTwoColumnTableNoteReplacer(MDSectionStrategy):
    """
    Преобразует двухколоночную таблицу вида:
    +--------------------------------+----------------------------------+
    | ![](path/to/image.png)         | Текст заметки                    |
    |                                | (может быть многострочным)       |
    +--------------------------------+----------------------------------+
    в {% note info %}...{% endnote %} без изображения и без символов '|'.
    """

    def transform_section(self, sec: Section) -> None:
        sec.body = self._transform_body(sec.body)  # старый метод transform переименован

    def _transform_body(self, content: str) -> str:
        lines = content.splitlines(keepends=True)
        new_lines = []
        i = 0
        while i < len(lines):
            # Ищем начало таблицы
            if re.match(r"^\+[-]+\+[-]+\+", lines[i].strip()):
                start_idx = i
                i += 1
                table_body = []
                # Собираем тело до закрывающего разделителя
                while i < len(lines) and not re.match(
                    r"^\+[-]+\+[-]+\+", lines[i].strip()
                ):
                    table_body.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1  # пропускаем закрывающий разделитель
                else:
                    # Нет закрывающей границы – оставляем как есть
                    new_lines.extend(lines[start_idx:i])
                    continue

                # Фильтруем строки, содержащие ячейки (с пайпом)
                cell_rows = [line for line in table_body if "|" in line]
                if not cell_rows:
                    new_lines.append("".join(lines[start_idx:i]))
                    continue

                right_text_parts = []
                for row in cell_rows:
                    # Удаляем пробелы в начале и конце строки
                    row = row.strip()
                    # Ищем первый и последний '|' в строке
                    first = row.find("|")
                    last = row.rfind("|")
                    if first == -1 or last == -1 or first == last:
                        continue
                    # Содержимое правой колонки: между первым и последним пайпом
                    # Но в двухколоночной таблице после первого пайпа идёт левая колонка,
                    # потом второй пайп, потом правая колонка, потом последний пайп.
                    # Поэтому нужно взять часть строки от второго пайпа до последнего.
                    # Найдём второй пайп (первый уже пропущен)
                    second = row.find("|", first + 1)
                    if second == -1:
                        # fallback: берём всё после первого пайпа
                        right = row[first + 1 : last].strip()
                    else:
                        right = row[second + 1 : last].strip()
                    # Удаляем одиночные пайпы, которые могут быть внутри текста (например, в ссылках или списках)
                    # Но не трогаем пайпы внутри ссылок: [текст](url) – там нет пайпов, только в таблицах.
                    # Просто удалим все пайпы, которые не являются частью Markdown-ссылки.
                    # Проще: заменить '|' на пробел, но аккуратно.
                    right = re.sub(
                        r"(?<!!)\|", " ", right
                    )  # заменяем |, если перед ним нет '!'
                    # Приводим множественные пробелы к одному
                    right = re.sub(r"\s+", " ", right).strip()
                    if right:
                        right_text_parts.append(right)

                full_text = " ".join(right_text_parts).strip()
                if full_text:
                    note = f"\n{{% note info %}}\n\n{full_text}\n\n{{% endnote %}}\n\n"
                    new_lines.append(note)
                else:
                    # Если текст пуст – оставляем исходную таблицу
                    new_lines.append("".join(lines[start_idx:i]))
            else:
                new_lines.append(lines[i])
                i += 1
        return "".join(new_lines)


class HorizontalRuleNoteStrategy(MDSectionStrategy):
    """
    Преобразует блоки вида:
    ------------------------------------------------------------------------------
    ![image.png](path)   ***Текст заметки***
    ------------------------------------------------------------------------------
    в {% note info %}...{% endnote %} без изображения.
    """

    def transform_section(self, sec: Section) -> None:
        sec.body = self._transform_body(sec.body)  # старый метод transform переименован

    def _transform_body(self, content: str) -> str:
        lines = content.splitlines(keepends=True)
        new_lines = []
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()
            # Строка-разделитель: состоит только из пробелов и дефисов, минимум 3 символа
            if re.match(r"^[\s\-]+$", stripped) and len(stripped) >= 3:
                start_idx = i
                i += 1
                block_lines = []
                # Собираем внутренность до следующего разделителя
                while i < len(lines) and not re.match(r"^[\s\-]+$", lines[i].strip()):
                    block_lines.append(lines[i])
                    i += 1
                if i < len(lines) and re.match(r"^[\s\-]+$", lines[i].strip()):
                    inner = "".join(block_lines).strip()
                    # Удаляем первое изображение в начале блока
                    img_pattern = re.compile(r"^\s*!\[.*?\]\(.*?\)\s*", re.DOTALL)
                    text_part = img_pattern.sub("", inner).strip()
                    if text_part:
                        note = (
                            f"\n{{% note info %}}\n\n{text_part}\n\n{{% endnote %}}\n\n"
                        )
                    else:
                        note = "\n{% note info %}\n\n{% endnote %}\n\n"
                    new_lines.append(note)
                    i += 1  # пропускаем закрывающий разделитель
                else:
                    # Нет закрывающего разделителя – оставляем как есть
                    new_lines.extend(lines[start_idx:i])
            else:
                new_lines.append(lines[i])
                i += 1
        return "".join(new_lines)
