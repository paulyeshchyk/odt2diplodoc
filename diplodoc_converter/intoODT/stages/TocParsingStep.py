from diplodoc_converter.intoODT.stages.OdtBuildContext import OdtBuildContext
from diplodoc_converter.intoODT.stages.OdtPipelineStep import OdtPipelineStep
from diplodoc_converter.intoODT.toc_parser import TocParser


class TocParsingStep(OdtPipelineStep):
    def execute(self, context: OdtBuildContext) -> None:
        root_toc = context.root_dir / "toc.yaml"
        if not root_toc.is_file():
            raise FileNotFoundError(f"Не найден корневой файл структуры: {root_toc}")

        parser = TocParser(context.root_dir)
        items = parser.load_toc(root_toc)

        if not items:
            raise ValueError(
                "Нет элементов для сборки (корневой toc.yaml пуст или повреждён)."
            )

        # Собираем дерево узлов и сохраняем в контекст
        context.nodes = parser.collect_md_files(context.root_dir, items, level=1)
        print(
            f"[Pipeline]: Структура оглавления успешно распарсена. Найдено корневых глав: {len(context.nodes)}"
        )
