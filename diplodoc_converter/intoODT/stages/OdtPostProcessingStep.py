from diplodoc_converter.intoODT.stages.OdtBuildContext import OdtBuildContext
from diplodoc_converter.intoODT.odt_postprocessor import (
    CrossReferenceStrategy,
    FigureCaptionStrategy,
    OdtPostProcessor,
)
from diplodoc_converter.intoODT.stages.OdtPipelineStep import OdtPipelineStep


class OdtPostProcessingStep(OdtPipelineStep):
    """Шаг 5: Постобработка структуры ODT (подписи к рисункам, перекрестные ссылки)."""

    def execute(self, context: OdtBuildContext) -> None:
        if not context.output_path.exists():
            print(
                f"[PostProcessor][Error]: Целевой файл {context.output_path} не найден для постобработки."
            )
            return

        strategies = [FigureCaptionStrategy(), CrossReferenceStrategy()]

        postproc = OdtPostProcessor(context.output_path)
        postproc.run(strategies)
        print("[Pipeline]: Постобработка ODT успешно завершена.")
