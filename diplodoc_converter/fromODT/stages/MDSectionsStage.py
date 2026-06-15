import re
from typing import Callable, List, Optional

from diplodoc_converter.fromODT.model.ConversionContext import ConversionContext
from diplodoc_converter.fromODT.model.ParserSettings import ParserSettings
from diplodoc_converter.fromODT.model.Section import Section, SectionType

from .base import Stage


class MDSectionsStage(Stage):
    def process(self, ctx: ConversionContext) -> None:
        print("Обработка секций ...")
        ctx.sections = self.parse_sections(ctx.markdown, ctx.config.parser_settings)
        if ctx.config.parser_settings.enable_section_indexing:
            should_index = ctx.config.parser_settings.indexing_callback
            if should_index is None:
                # По умолчанию индексируем секции, у которых section_type не None (т.е. распознан тип)
                def default_should_index(sec) -> bool:
                    return sec.section_type is not None

                should_index = default_should_index

            SectionIndexAssigner.assign_section_indices(
                ctx.sections,
                lambda sec: sec.section_type is not None,
                ctx.config.parser_settings.inherit_index_from_nonindexed,
            )

    def parse_sections(
        self,
        markdown_content: str | None,
        parser_settings: ParserSettings | None = None,
    ) -> Optional[List[Section]]:
        if not markdown_content:
            return None

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

        heading_re = re.compile(r"^(#{1,6})\s+(.*)$")

        def flush():
            nonlocal current_section, current_body_lines
            if current_section is not None:
                current_section.body = "\n".join(current_body_lines).strip()
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
                anchor = AnchorExtractor.extract_anchor(raw_title)
                cleaned = HeaderCleaner.clean_heading(raw_title)

                if not cleaned:
                    if current_section is not None:
                        current_body_lines.append(line)
                    continue

                if level <= max_level:
                    flush()

                    section_type, number, pure_title = HeaderParser.parse_heading(
                        cleaned
                    )
                    current_section = Section(
                        title=cleaned,
                        pureTitle=pure_title,
                        level=level,
                        body="",
                        children=[],
                        anchor=anchor,
                        section_type=section_type,
                        sectionIndex=number,
                    )
                else:
                    if current_section is not None:
                        current_body_lines.append(line)
            else:
                if current_section is not None:
                    current_body_lines.append(line)

        flush()
        return root_sections


class SectionFlatten:
    @staticmethod
    def flatten_sections(
        sections: Optional[List[Section]],
    ) -> List[Section]:
        if not sections:
            return []
        result = []

        def walk(sec: Section):
            result.append(sec)
            for child in sec.children:
                walk(child)

        for sec in sections:
            walk(sec)
        return result


class SectionIndexAssigner:
    @staticmethod
    def assign_section_indices(
        sections: List[Section] | None,
        should_index: Callable[[Section], bool],
        inherit_nonindexed: bool,
    ) -> None:
        """
        Рекурсивно присваивает sectionIndex каждой секции.
        :param should_index: функция, возвращающая True, если секция должна иметь индекс.
        :param inherit_nonindexed: если True, то у потомков неиндексируемой секции индекс тоже None.
                                Если False, то потомки индексируются заново (начиная с 1).
        """

        def process(sec_list: List[Section] | None, parent_index: Optional[str] = None):
            counter = 1
            if not sec_list:
                return

            for sec in sec_list:
                if should_index(sec):
                    sec.sectionIndex = (
                        f"{parent_index}.{counter}" if parent_index else str(counter)
                    )
                    counter += 1
                else:
                    sec.sectionIndex = ""
                # Обработка детей
                if sec.children:
                    if should_index(sec) or not inherit_nonindexed:
                        # Если текущая секция индексируемая, передаём её индекс детям
                        # Если неиндексируемая и inherit_nonindexed=False, то дети начинают с нуля (parent_index=None)
                        process(sec.children, sec.sectionIndex)
                    else:
                        # inherit_nonindexed=True и секция не индексируемая → дети тоже не получают индекса
                        process(sec.children, None)

        process(sections)


class HeaderParser:
    @staticmethod
    def parse_heading(heading: str) -> tuple[SectionType, Optional[str], str]:
        # 1. Ищем с типом (русский/английский)
        type_patterns = {
            SectionType.PART: r"(?:Часть|Part)\s+(\d+)\.\s*(.*)",
            SectionType.SECTION: r"(?:Раздел|Section)\s+(\d+)\.\s*(.*)",
            SectionType.CHAPTER: r"(?:Глава|Chapter)\s+(\d+)\.\s*(.*)",
        }
        for stype, pattern in type_patterns.items():
            match = re.match(pattern, heading, re.IGNORECASE)
            if match:
                number = match.group(1)
                rest = match.group(2).strip()
                return stype, number, rest

        # 2. Ищем номер без типа (например, "1.2. Текст" или "1. Текст")
        match = re.match(r"^(\d+(?:\.\d+)*)\.\s+(.*)", heading)
        if match:
            number = match.group(1)  # например "1.2"
            rest = match.group(2).strip()
            return SectionType.PAGE, number, rest

        # 3. Ни типа, ни номера
        return SectionType.PAGE, None, heading


class AnchorExtractor:
    @staticmethod
    def extract_anchor(raw: str) -> str | None:
        """Извлекает якорь вида anchor-123 из конструкции []{#anchor-123}."""
        match = re.search(r"\[\]\{#(anchor-\d+)\}", raw)
        return match.group(1) if match else None


class HeaderCleaner:
    @staticmethod
    def clean_heading(raw: str) -> str:
        """Очищает заголовок от мусора Pandoc, но оставляет якорь для отдельного извлечения."""
        # Удаляем HTML-теги
        s = re.sub(r"<[^>]+>", "", raw)
        # Удаляем конструкции [текст]{#anchor} и []{#anchor}
        s = re.sub(r"\[[^\]]*\]\{#[^}]+\}", "", s)
        # Удаляем оставшиеся [] и {}
        s = re.sub(r"\[\]|\{\}", "", s)
        # Удаляем голые слова anchor-123
        s = re.sub(r"\banchor[-_][0-9]+\b", "", s)
        # Убираем лишние пробелы
        s = re.sub(r"\s+", " ", s).strip()
        return s
