# odt_builder.py

import tempfile
from pathlib import Path
from typing import List

from diplodoc_converter.intoODT.stages import OdtBuildContext, OdtPipelineStep


class OdtBuilderPipeline:
    """Управляет конфигурацией шагов сборки и их последовательным выполнением."""

    def __init__(self, steps: List[OdtPipelineStep]):
        self.steps = steps

    def build(self, root_dir: Path, output_path: Path) -> None:
        # Инициализируем контекст без nodes
        context = OdtBuildContext(
            root_dir=root_dir,
            output_path=output_path,
        )

        print("[OdtBuilderPipeline]: Запуск конвейера сборки...")

        with tempfile.TemporaryDirectory() as temp_dir:
            context.temp_dir = Path(temp_dir)

            # Последовательно гоним контекст по шагам
            for step in self.steps:
                step.execute(context)

                # Защитная проверка: если после шага парсинга (или любого другого) узлов нет,
                # прерываем выполнение.
                if not context.nodes:
                    print("[OdtBuilderPipeline]: Нет элементов для сборки. Остановка.")
                    return

        print(
            f"[OdtBuilderPipeline]: Сборка завершена успешно! Результат: {output_path}"
        )
