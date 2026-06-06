# diplodoc_converter/converter.py
import shutil
from pathlib import Path
from .pandoc_wrapper import convert_odt_to_markdown
from .section_parser import parse_sections, flatten_sections
from .image_processor import extract_and_replace_images
from .link_processor import build_slug_map, replace_internal_links
from .diplodoc_writer import write_section_tree
from .cache_settings import CacheSettings

def convert_odt_to_diplodoc(odt_path: str, output_dir: str, cache_settings: CacheSettings | None = None) -> None:
    """
    Конвертирует ODT в структуру Diplodoc.
    
    Параметры:
        odt_path: путь к исходному .odt файлу
        output_dir: папка для результата (создаст иерархию внутри)
        cache_settings: объект CacheSettings (если не указан, используются значения по умолчанию)
    """
    if cache_settings is None:
        cache_settings = CacheSettings()   # все параметры по умолчанию
    
    # Запускаем pandoc либо читаем из кэша
    markdown_content = build_markdown(odt_path, cache_settings)
    
    # Разбор структуры документа
    sections = parse_sections(markdown_content)
    if not sections:
        raise ValueError("Не найдено ни одного заголовка H1.")
    
    output_dir_absolute = Path(output_dir).absolute()

    # Построить slug_map (он же присвоит slug каждой секции)
    slug_map = build_slug_map(sections, output_dir_absolute)
    
    # Обработка изображений и ссылок
    temp_dir1 = Path(cache_settings.temp_dir).absolute()
    temp_media1 = temp_dir1 / "media"
    build_links_and_images(temp_media1, sections, output_dir_absolute, slug_map)
    
    # Создание структуры Diplodoc
    print("Создание структуры Diplodoc...")
    write_section_tree(sections, output_dir_absolute, root_title="Документация")
    
    wipe_cache_if_need(cache_settings)
    
    print(f"Готово! Результат в {output_dir}")

def build_links_and_images(temp_media1, sections, output_dir_absolute, slug_map):
    print("Обработка изображений и внутренних ссылок...")
    for sec in flatten_sections(sections):
        target_images_dir = output_dir_absolute / sec.slug / "images"
        sec.body, img_cnt = extract_and_replace_images(sec.body, temp_media1, target_images_dir)
        if img_cnt:
            print(f"  {sec.title}: {img_cnt} изображений")
        sec.body = replace_internal_links(sec.body, slug_map, sec.slug)

def wipe_cache_if_need(cache_settings):
    temp_dir = Path(cache_settings.temp_dir).absolute()
    # Очистка временной папки, если не нужно сохранять кэш
    if not cache_settings.keep_cache and temp_dir.exists():
        print("Удаляем временные файлы...")
        shutil.rmtree(temp_dir, ignore_errors=True)
    elif cache_settings.keep_cache and temp_dir.exists():
        print(f"Временные файлы сохранены в {temp_dir}")

def build_markdown(odt_path, cache_settings):
    """Возвращает содержимое Markdown (из кэша или через pandoc)."""

    temp_dir = Path(cache_settings.temp_dir).absolute()
    temp_md = temp_dir / "full_doc.md"
    
    if cache_settings.reuse_cache and temp_md.exists():
        print(f"Используем существующий кэш: {temp_md}")
        markdown_content = temp_md.read_text(encoding='utf-8')
    else:
        print("Конвертация ODT в Markdown через Pandoc...")
        # Если reuse_cache включён, но файла нет – всё равно вызываем pandoc
        # Предварительно убедимся, что временная папка чистая (если не reuse_cache или нет кэша)
        if not cache_settings.reuse_cache and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir.mkdir(parents=True, exist_ok=True)
        odt_path_absolute = Path(odt_path).absolute()
        temp_media = temp_dir / "media"
        try:
            markdown_content = convert_odt_to_markdown(odt_path_absolute, temp_md, temp_media)
        except Exception as e:
            print(f"Ошибка Pandoc: {e}")
            raise
    return markdown_content