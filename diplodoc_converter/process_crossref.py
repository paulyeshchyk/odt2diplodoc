import re
import json
import zipfile
import tempfile
from pathlib import Path
from lxml import etree

from .figure_constants import (
    FIGURE_PREFIX, FIGURE_MARKER
)

NAMESPACES = {
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
    'xlink': 'http://www.w3.org/1999/xlink',
}

def process_odt_crossrefs(odt_path: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        with zipfile.ZipFile(odt_path, 'r') as zf:
            zf.extractall(tmp_path)
        
        content_xml = tmp_path / 'content.xml'
        tree = etree.parse(str(content_xml))
        root = tree.getroot()
        
        fig_map = {}
        ref_map = {}
        
        # Этап 1: сбор рисунков и добавление меток {#fig:N}
        for frame in root.xpath('.//draw:frame', namespaces=NAMESPACES):
            seq = frame.find('.//text:sequence', namespaces=NAMESPACES)
            if seq is None:
                continue
            num = seq.text.strip()
            ref_name = seq.get(f'{{{NAMESPACES["text"]}}}ref-name')
            if ref_name:
                ref_map[ref_name] = num
            img = frame.find('.//draw:image', namespaces=NAMESPACES)
            if img is not None:
                img_href = img.get(f'{{{NAMESPACES["xlink"]}}}href')
                fig_map[num] = img_href
            
            # Добавляем метку {#fig:N} в подпись
            para = seq
            while para is not None and para.tag != f'{{{NAMESPACES["text"]}}}p':
                para = para.getparent()
            if para is not None:
                current_text = etree.tostring(para, encoding='unicode', method='text')
                marker = f'{{#{FIGURE_MARKER}:{num}}}'
                if marker not in current_text:
                    span = etree.Element(f'{{{NAMESPACES["text"]}}}span')
                    span.text = f' {marker}'
                    para.append(span)
        
        # Этап 2: замена sequence-ref на (рис. N)
        for seq_ref in root.xpath('.//text:sequence-ref', namespaces=NAMESPACES):
            ref_name = seq_ref.get(f'{{{NAMESPACES["text"]}}}ref-name')
            if ref_name and ref_name in ref_map:
                num = ref_map[ref_name]
                parent = seq_ref.getparent()
                new_span = etree.Element(f'{{{NAMESPACES["text"]}}}span')
                new_span.text = f'({FIGURE_PREFIX} {num})'
                parent.replace(seq_ref, new_span)
        
        tree.write(str(content_xml), encoding='utf-8', xml_declaration=True)
        
        with zipfile.ZipFile(odt_path, 'w') as zf:
            for file_path in tmp_path.rglob('*'):
                zf.write(file_path, arcname=file_path.relative_to(tmp_path))
        
        print(f"[DEBUG] Всего рисунков найдено: {len(fig_map)}")
        return fig_map