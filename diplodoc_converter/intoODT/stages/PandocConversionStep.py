from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.stages.OdtBuildContext import OdtBuildContext
from diplodoc_converter.intoODT.stages.OdtPipelineStep import OdtPipelineStep


import os
import subprocess
from pathlib import Path


class PandocConversionStep(OdtPipelineStep):
    """Шаг 4: Конвертация combined.md в результирующий ODT документ при помощи Pandoc."""

    def execute(self, context: OdtBuildContext) -> None:
        cmd = [
            "pandoc",
            str(context.combined_md_path),
            "-o",
            str(context.output_path.absolute()),
            "--resource-path",
            str(context.temp_dir),
            "--standalone",
        ]

        if MdToOdtConfig.REFERENCE_ODT and Path(MdToOdtConfig.REFERENCE_ODT).is_file():
            cmd.extend(
                [
                    "--reference-doc",
                    str(Path(MdToOdtConfig.REFERENCE_ODT).resolve()),
                ]
            )

        try:
            print(f"[Pandoc]: Начат. Команда: {' '.join(cmd)}")
            current_env = os.environ.copy()
            current_env["PYTHONUTF8"] = "1"

            subprocess.run(cmd, check=True, cwd=context.temp_dir, env=current_env)
            print(f"[Pandoc]: Закончен. Выходной файл: {context.output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка pandoc: {e}")
            raise e
        except FileNotFoundError:
            print("Pandoc не установлен в системе")
            raise
