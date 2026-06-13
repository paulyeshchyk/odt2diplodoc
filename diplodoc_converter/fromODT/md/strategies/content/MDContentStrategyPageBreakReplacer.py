from .MDContentStrategy import MDContentStrategy


class MDContentStrategyPageBreakReplacer(MDContentStrategy):
    def transform(self, content: str) -> str:
        # Заменяем маркер на три тега <br> (можно изменить на нужный HTML/CSS)
        return content.replace("@@@PAGE_BREAK@@@", "<br/><br/><br/>")
