import re


class MDNotesProcessor:
    @staticmethod
    def replace_note_blocks(content: str) -> str:
        """Заменяет {% note ... %} на fenced div с custom-style."""

        def replacer(match):
            note_type = match.group(1).lower()
            title = match.group(2)  # может быть None
            inner = match.group(3).strip()

            style_map = {
                "tip": "NoteTip",
                "warning": "NoteWarning",
                "alert": "NoteAlert",
                "info": "NoteInfo",
            }
            style = style_map.get(note_type, "Note")

            # Если есть заголовок, добавим его жирным в начало содержимого
            if title:
                inner = f"**{title}**\n\n{inner}"

            return f'::: {{custom-style="{style}"}}\n{inner}\n:::'

        pattern = r'\{% note (\w+)(?:\s+"([^"]+)")?\s*%\}(.*?)\{% endnote %\}'
        return re.sub(pattern, replacer, content, flags=re.DOTALL)
