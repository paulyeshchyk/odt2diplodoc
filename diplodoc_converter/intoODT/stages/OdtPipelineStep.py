from abc import ABC, abstractmethod

from diplodoc_converter.intoODT.stages.OdtBuildContext import OdtBuildContext


class OdtPipelineStep(ABC):
    """Абстрактный класс для всех шагов конвейера сборки ODT."""

    @abstractmethod
    def execute(self, context: OdtBuildContext) -> None:
        """Выполнить логику конкретного этапа над переданным контекстом."""
        pass
