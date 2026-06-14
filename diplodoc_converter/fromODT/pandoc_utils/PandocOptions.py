# diplodoc_converter/config.py

from dataclasses import dataclass
from typing import Optional

from diplodoc_converter.fromODT.pandoc_utils.LuaOptions import LuaOptions


@dataclass
class PandocOptions:
    """
    Настройки формата вывода Pandoc.
    """

    format: str = "markdown"
    pipe_tables: Optional[bool] = None
    backtick_code_blocks: Optional[bool] = None
    link_attributes: Optional[bool] = None
    raw_html: Optional[bool] = None
    raw_format: Optional[str] = None
    lua_options: Optional[LuaOptions] = None

    def to_pandoc_string(self) -> str:
        """Формирует строку вида "markdown+pipe_tables-raw_html"."""
        if self.raw_format is not None:
            return self.raw_format

        result = self.format
        for field_name, field_value in self.__dict__.items():
            if (
                field_name in ("format", "raw_format", "lua_options")
                or field_value is None
            ):
                continue
            if field_value:
                result += f"+{field_name}"
            else:
                result += f"-{field_name}"
        return result
