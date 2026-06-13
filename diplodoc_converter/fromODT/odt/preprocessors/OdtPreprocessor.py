from abc import ABC
from pathlib import Path


class OdtPreprocessor(ABC):
    def process(self, odt_path: Path) -> None:
        pass
