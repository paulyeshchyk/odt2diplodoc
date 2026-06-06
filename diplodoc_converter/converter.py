# diplodoc_converter/converter.py

import shutil
from pathlib import Path
from typing import List

from .config import PandocOptions
from .strategies.base import TransformationStrategy
from .pandoc_wrapper import convert_odt_to_markdown
from .section_parser import Section, parse_sections, flatten_sections
from .image_processor import extract_and_replace_images
from .link_processor import build_slug_and_anchor_maps, replace_internal_links
from .diplodoc_writer import write_section_tree
from .config import CacheSettings, ConversionConfig
from .strategies.note_blocks import HorizontalRuleNoteStrategy, TwoColumnTableNoteStrategy
from .strategies.figure_wrapper import WrapImagesInFiguresStrategy
from .strategies.remove_pandoc_attrs import RemovePandocAttributesStrategy

def convert_odt_to_diplodoc(config: ConversionConfig) -> None:
    if config.cache_settings is None:
        config.cache_settings = CacheSettings()
    
    markdown_content = build_markdown(config.odt_path, config.cache_settings, config.pandoc_options)
    markdown_content = apply_preprocessing_pipeline(markdown_content)

    print("Разбор структуры документа...")
    sections = parse_sections(markdown_content, config.parser_settings)
    if not sections:
        raise ValueError("Не найдено ни одного заголовка H1.")
    
    output_dir_absolute = Path(config.output_dir).absolute()
    
    # Обработка внутренних ссылок (изменяет sec.body)
    slug_map, anchor_map = build_slug_and_anchor_maps(sections, output_dir_absolute)
    process_internal_links(sections, slug_map, anchor_map)   # ← передаём оба
    
    # Копирование изображений и обновление sec.body
    temp_media_dir = Path(config.cache_settings.temp_dir).absolute() / "media"
    copy_images_to_sections(sections, output_dir_absolute, temp_media_dir)
    clean_pandoc_attributes(sections)
    apply_note_strategies_to_sections(sections)
    
    # Обёртываем изображения в <figure> (добавляем)
    
    wrap_images_in_figures(sections)

    # Запись всей структуры (с уже обновлёнными sec.body)
    print("Создание структуры Diplodoc...")
    write_section_tree(sections, output_dir_absolute, root_title="Документация")
    
    wipe_cache_if_need(config.cache_settings)
    print(f"Готово! Результат в {config.output_dir}")

def build_markdown(odt_path: str, cache_settings: CacheSettings, pandoc_options: PandocOptions) -> str:
    temp_dir = Path(cache_settings.temp_dir).absolute()
    temp_md = temp_dir / "full_doc.md"
    
    if cache_settings.reuse_cache and temp_md.exists():
        print(f"Используем существующий кэш: {temp_md}")
        return temp_md.read_text(encoding='utf-8')
    
    print("Конвертация ODT в Markdown через Pandoc...")
    if not cache_settings.reuse_cache and temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    odt_path_absolute = Path(odt_path).absolute()
    temp_media = temp_dir / "media"
    try:
        return convert_odt_to_markdown(odt_path_absolute, temp_md, temp_media, pandoc_options)
    except Exception as e:
        print(f"Ошибка Pandoc: {e}")
        raise

def process_internal_links(sections: List[Section], slug_map, anchor_map):
    print("Обработка внутренних ссылок...")
    for sec in flatten_sections(sections):
        # sec.full_slug – это Path, нужно преобразовать в строку с прямыми слешами
        sec.body = replace_internal_links(sec.body, slug_map, anchor_map, str(sec.full_slug).replace('\\', '/'))

def copy_images_to_sections(sections: List[Section], output_root: Path, temp_media_dir: Path):
    """Рекурсивно копирует изображения в папки images секций и обновляет sec.body."""
    print("Копирование изображений...")
    def process(sec: Section, current_path: Path):
        target_images_dir = current_path / "media"
        new_body, img_cnt = extract_and_replace_images(sec.body, temp_media_dir, target_images_dir)
        if img_cnt:
            print(f"  {sec.title}: {img_cnt} изображений")
            sec.body = new_body
        for child in sec.children:
            process(child, current_path / child.slug)
    
    for sec in sections:
        process(sec, output_root / sec.slug)

def wipe_cache_if_need(cache_settings: CacheSettings):
    temp_dir = Path(cache_settings.temp_dir).absolute()
    if not cache_settings.keep_cache and temp_dir.exists():
        print("Удаляем временные файлы...")
        shutil.rmtree(temp_dir, ignore_errors=True)
    elif cache_settings.keep_cache and temp_dir.exists():
        print(f"Временные файлы сохранены в {temp_dir}")

def apply_preprocessing_pipeline(content: str) -> str:
    from .strategies.pipeline import Pipeline
    from .strategies.remove_empty_anchors import RemoveEmptyAnchorsStrategy
    strategies: List[TransformationStrategy] = [
        RemoveEmptyAnchorsStrategy(),
    ]
    pipeline = Pipeline(strategies)
    return pipeline.run(content)

def apply_note_strategies_to_sections(sections: List[Section]) -> None:
    """Применяет стратегии преобразования блоков в заметки ко всем секциям."""
    print("Преобразование блоков в заметки Diplodoc...")
    hline_strategy = HorizontalRuleNoteStrategy()
    table_strategy = TwoColumnTableNoteStrategy()
    for sec in flatten_sections(sections):
        # Сначала обрабатываем горизонтальные линии
        sec.body = hline_strategy.transform(sec.body)
        # Затем таблицы с картинками
        sec.body = table_strategy.transform(sec.body)

def wrap_images_in_figures(sections: List[Section]) -> None:
    """Оборачивает все изображения в HTML-теги <figure> с подписью."""
    print("Обёртка изображений в <figure>...")
    strategy = WrapImagesInFiguresStrategy()
    for sec in flatten_sections(sections):
        sec.body = strategy.transform(sec.body)

def clean_pandoc_attributes(sections: List[Section]) -> None:
    print("Удаление атрибутов Pandoc вида {alt=\"...\"}...")
    strategy = RemovePandocAttributesStrategy()
    for sec in flatten_sections(sections):
        sec.body = strategy.transform(sec.body)