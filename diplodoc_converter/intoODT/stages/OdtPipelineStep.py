from diplodoc_converter.intoODT.stages.OdtBuildContext import OdtBuildContext


from abc import ABC, abstractmethod


class OdtPipelineStep(ABC):
    """Абстрактный класс для всех шагов конвейера сборки ODT."""

    @abstractmethod
    def execute(self, context: OdtBuildContext) -> None:
        """Выполнить логику конкретного этапа над переданным контекстом."""
        pass
