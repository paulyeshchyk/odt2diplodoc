import re

from PIL import Image

from diplodoc_converter.intoODT.config import MdToOdtConfig
from diplodoc_converter.intoODT.preprocessing.MD.DocNodeUtils import DocNodeUtils
from diplodoc_converter.intoODT.preprocessing.MD.ProcessingContext import (
    ProcessingContext,
)


class ImageProcessor:
    @staticmethod
    def process(ctx: ProcessingContext) -> None:
        if not ctx.current_node.path:
            return
        ctx.content = ImageProcessor._process_images(ctx.content, ctx)

    @staticmethod
    def _process_images(content: str, ctx: ProcessingContext) -> str:
        def replace_path(match):
            alt_text = match.group(1).strip()
            img_src = match.group(2).strip()
            figure_html = match.group(4) if match.group(4) else ""

            extracted_caption = ""
            if figure_html:
                caption_match = re.search(
                    r"<figcaption[^>]*>(.*?)</figcaption>", figure_html, re.DOTALL
                )
                if caption_match:
                    raw_caption = caption_match.group(1)
                    cleaned = re.sub(r"<[^>]+>", "", raw_caption).strip()
                    extracted_caption = re.sub(
                        r"^(Рисунок|Рис)\s*\d+\.\s*", "", cleaned, flags=re.IGNORECASE
                    ).strip()

            # Нормализация путей
            img_src = re.sub(r"/+", "/", img_src)
            img_src = re.sub(r"^\./", "", img_src)

            parent = DocNodeUtils.getDocNode_parent_dir(ctx.current_node)
            abs_img = (parent / img_src).resolve()
            try:
                rel_img = abs_img.relative_to(ctx.root_dir)
            except ValueError:
                return match.group(0)

            rel_img = MdToOdtConfig.normalize_rel_path(rel_img)
            rel_img_str = "./" + rel_img.as_posix()
            rel_img_str = re.sub(r"/\./", "/", rel_img_str)
            rel_img_str = re.sub(r"/+", "/", rel_img_str)

            full_img_path = ctx.temp_dir / rel_img
            width = 0
            if full_img_path.exists():
                try:
                    with Image.open(full_img_path) as img:
                        width = img.width
                except Exception:
                    pass

            final_caption_text = extracted_caption if extracted_caption else alt_text

            if MdToOdtConfig.CAPTION_POSITION == "inside":
                size_attr = (
                    "{{ width=100% }}" if width > MdToOdtConfig.WIDTH_THRESHOLD else ""
                )
                markdown_image = f"![]({rel_img_str}){size_attr}"
                if final_caption_text:
                    markdown_image += (
                        f" %%%CAPTION_START%%%{final_caption_text}%%%CAPTION_END%%%"
                    )
                return markdown_image
            else:
                size_attr = (
                    "{ width=100% }" if width > MdToOdtConfig.WIDTH_THRESHOLD else ""
                )
                return f"![{final_caption_text}]({rel_img_str}){size_attr}"

        pattern = (
            r"!\[([^\]]*)\]\(([^)]+)\)(\s*\{[^}]+\})?(?:\s*(<figure>.*?</figure>))?"
        )
        return re.sub(pattern, replace_path, content, flags=re.DOTALL)
