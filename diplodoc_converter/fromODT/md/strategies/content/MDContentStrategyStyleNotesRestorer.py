import re
from .MDContentStrategy import MDContentStrategy


class MDContentStrategyStyleNotesRestorer(MDContentStrategy):
    def transform(self, content: str) -> str:
        pattern = r"@@@NOTE_(\w+)\\\|\\\|(.*?)\\\|\\\|(.*?)@@@"

        def repl(m):
            note_type = m.group(1).lower()
            title = m.group(2).strip()
            body = m.group(3).strip()
            # Убираем возможные экранирования внутри (на всякий случай)
            body = body.replace(r"\|", "|")
            return f'{{% note {note_type} "{title}" %}}\n\n{body}\n\n{{% endnote %}}'

        return re.sub(pattern, repl, content, flags=re.DOTALL)
