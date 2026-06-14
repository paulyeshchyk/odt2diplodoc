#!/usr/bin/env python3
# diplodoc_converter/utils.py

import re


class Slugify_Utils:
    @staticmethod
    def slugify(text: str, max_length: int = 50) -> str:
        """Превращает заголовок в безопасное имя для папки/файла."""
        s = re.sub(r"[^\w\s-]", "", text.lower())
        s = re.sub(r"[-\s]+", "_", s).strip("-_")
        return s[:max_length]
