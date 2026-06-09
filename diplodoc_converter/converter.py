# diplodoc_converter/converter.py
import json
import shutil
from pathlib import Path
from typing import List

from .config import CacheSettings, ConversionConfig
from .diplodoc_writer import write_section_tree
from .image_processor import extract_and_replace_images
from .link_processor import build_slug_and_anchor_maps, replace_internal_links
from .pandoc_wrapper import convert_odt_to_markdown
from .process_crossref import process_odt_crossrefs
from .section_parser import Section, flatten_sections, parse_sections
from .strategies import global_strategies, section_strategies


class ConverterSettings:
    """Константы, используемые в конвертере."""
    MEDIA_DIR = "media"
    TEMP_MD_FILENAME = "full_doc.md"
    TEMP_ODT_FILENAME = "crossref_input.odt"
    FIG_MAP_EXT = ".figmap.json"
    ROOT_TITLE = "Документация"


class ConverterMessages:
    """Локализованные сообщения для пользователя."""
    def __init__(self, lang="ru"):
        self.lang = lang
        # Здесь можно расширить под другие языки
        self.msgs = {
            "ru": {
                "parsing": "Разбор структуры документа...",
                "no_h1": "Не найдено ни одного заголовка H1.",
                "internal_links": "Обработка внутренних ссылок...",
                "copying_images": "Копирование изображений...",
                "writing_tree": "Создание структуры Diplodoc...",
                "done": "Готово! Результат в {output_dir}",
                "using_cache": "Используем существующий кэш: {path}",
                "pandoc_start": "Конвертация ODT в Markdown через Pandoc...",
                "wipe_output": "Удаляем каталог вывода...",
                "wipe_cache": "Удаляем временные файлы...",
                "cache_kept": "Временные файлы сохранены в {path}",
                "pandoc_error": "Ошибка Pandoc: {error}",
                "fig_map_warning": "fig_map.json не найден, замена ссылок не выполнена.",
                "fig_map_empty_warning": "fig_map пуст, замена ссылок не будет выполнена.",
                "crossref_enabled": "Обработка перекрёстных ссылок включена.",
            }
        }

    def get(self, key, **kwargs):
        msg = self.msgs.get(self.lang, self.msgs["ru"]).get(key, key)
        return msg.format(**kwargs) if kwargs else msg


messages = ConverterMessages(lang="ru")


def convert_odt_to_diplodoc(config: ConversionConfig) -> None:
    if config.cache_settings is None:
        config.cache_settings = CacheSettings()

    wipe_output_if_need(config)

    markdown_content = build_markdown(config)
    for strategy in global_strategies:
        markdown_content = strategy.transform(markdown_content)

    print(messages.get("parsing"))
    sections = parse_sections(markdown_content, config.parser_settings)
    if not sections:
        raise ValueError(messages.get("no_h1"))

    output_dir_absolute = Path(config.output_dir).absolute()

    process_internal_links_for_sections(sections, output_dir_absolute)

    temp_media_dir = Path(config.cache_settings.temp_dir).absolute() / ConverterSettings.MEDIA_DIR
    copy_images_to_sections(sections, output_dir_absolute, temp_media_dir)

    if getattr(config.pandoc_options, 'enable_crossref', False):
        # Загружаем fig_map из сохранённого JSON
        temp_odt = Path(config.cache_settings.temp_dir).absolute() / ConverterSettings.TEMP_ODT_FILENAME
        fig_map_path = temp_odt.with_suffix(ConverterSettings.FIG_MAP_EXT)
        if fig_map_path.exists():
            with open(fig_map_path, 'r', encoding='utf-8') as f:
                fig_map = json.load(f)
            replace_crossref_links(sections, fig_map, output_dir_absolute)
        else:
            print(messages.get("fig_map_warning"))

    for strategy in section_strategies:
        for sec in flatten_sections(sections):
            strategy.transform_section(sec)

    print(messages.get("writing_tree"))
    write_section_tree(sections, output_dir_absolute, root_title=ConverterSettings.ROOT_TITLE)
    wipe_cache_if_need(config.cache_settings)
    print(messages.get("done", output_dir=config.output_dir))


def process_internal_links_for_sections(sections: List[Section], output_dir: Path) -> None:
    print(messages.get("internal_links"))
    slug_map, anchor_map = build_slug_and_anchor_maps(sections, output_dir)
    for sec in flatten_sections(sections):
        sec.body = replace_internal_links(sec.body, slug_map, anchor_map, str(sec.full_slug).replace("\\", "/"))


def build_markdown(config: ConversionConfig) -> str:
    cache = config.cache_settings
    temp_dir = Path(cache.temp_dir).absolute()
    temp_md = temp_dir / ConverterSettings.TEMP_MD_FILENAME

    if cache.reuse_cache and temp_md.exists():
        print(messages.get("using_cache", path=temp_md))
        return temp_md.read_text(encoding="utf-8")

    working_path = config.odt_path
    enable_crossref = getattr(config.pandoc_options, 'enable_crossref', False)
    if enable_crossref:
        print(messages.get("crossref_enabled"))
        temp_odt = temp_dir / ConverterSettings.TEMP_ODT_FILENAME
        temp_odt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config.odt_path, temp_odt)
        fig_map = process_odt_crossrefs(temp_odt)
        fig_map_path = temp_odt.with_suffix(ConverterSettings.FIG_MAP_EXT)
        with open(fig_map_path, 'w', encoding='utf-8') as f:
            json.dump(fig_map, f)
        working_path = str(temp_odt)

    print(messages.get("pandoc_start"))
    temp_dir.mkdir(parents=True, exist_ok=True)
    odt_path_absolute = Path(working_path).absolute()
    temp_media = temp_dir / ConverterSettings.MEDIA_DIR
    try:
        return convert_odt_to_markdown(odt_path_absolute, temp_md, temp_media, config.pandoc_options)
    except Exception as e:
        print(messages.get("pandoc_error", error=e))
        raise


def copy_images_to_sections(sections: List[Section], output_root: Path, temp_media_dir: Path) -> None:
    print(messages.get("copying_images"))

    def process(sec: Section, current_path: Path):
        target_images_dir = current_path / ConverterSettings.MEDIA_DIR
        new_body, _ = extract_and_replace_images(sec.body, temp_media_dir, target_images_dir)
        sec.body = new_body
        for child in sec.children:
            process(child, current_path / child.slug)

    for sec in sections:
        process(sec, output_root / sec.slug)


def replace_crossref_links(sections: List[Section], fig_map: dict, output_root: Path) -> None:
    if not fig_map:
        print(messages.get("fig_map_empty_warning"))
        return

    media_paths = {num: f"{ConverterSettings.MEDIA_DIR}/{Path(src_path).name}" for num, src_path in fig_map.items()}

    for num, media_path in media_paths.items():
        old = f'[@fig:{num}]'
        new = f'[{num}]({media_path})'
        for sec in flatten_sections(sections):
            if old in sec.body:
                sec.body = sec.body.replace(old, new)


def wipe_cache_if_need(cache_settings: CacheSettings) -> None:
    temp_dir = Path(cache_settings.temp_dir).absolute()
    if not cache_settings.keep_cache and temp_dir.exists():
        print(messages.get("wipe_cache"))
        shutil.rmtree(temp_dir, ignore_errors=True)
    elif cache_settings.keep_cache and temp_dir.exists():
        print(messages.get("cache_kept", path=temp_dir))


def wipe_output_if_need(config: ConversionConfig) -> None:
    output_dir = Path(config.output_dir).absolute()
    if output_dir.exists():
        print(messages.get("wipe_output"))
        shutil.rmtree(output_dir, ignore_errors=True)