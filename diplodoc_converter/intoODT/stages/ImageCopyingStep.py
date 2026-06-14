from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.models import DocNode
from diplodoc_converter.intoODT.stages.OdtBuildContext import OdtBuildContext
from diplodoc_converter.intoODT.stages.OdtPipelineStep import OdtPipelineStep


import shutil
from pathlib import Path
from typing import List


class ImageCopyingStep(OdtPipelineStep):
    """Шаг 2: Рекурсивный сбор и копирование изображений во временную директорию."""

    def execute(self, context: OdtBuildContext) -> None:
        copied_folders: set[Path] = set()
        self._copy_images_for_nodes(
            context.nodes, context.temp_dir, context.root_dir, copied_folders
        )
        print("[Pipeline]: Ресурсы и картинки скопированы во временную директорию.")

    def _copy_images_for_nodes(
        self,
        nodes: List[DocNode],
        temp_path: Path,
        root_dir: Path,
        copied_folders: set,
    ):
        for node in nodes:
            if node.path:
                src_folder = node.path.parent
                if src_folder not in copied_folders:
                    for item in src_folder.rglob("*"):
                        if (
                            item.is_file()
                            and item.suffix.lower() in MdToOdtConfig.IMAGE_EXTENSIONS
                        ):
                            try:
                                rel_path = item.relative_to(root_dir)
                                rel_path = MdToOdtConfig.normalize_rel_path(rel_path)
                            except ValueError:
                                continue
                            dest_file = temp_path / rel_path
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dest_file)
                    copied_folders.add(src_folder)
            if node.children:
                self._copy_images_for_nodes(
                    node.children, temp_path, root_dir, copied_folders
                )
