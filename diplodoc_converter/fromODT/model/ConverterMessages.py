class ConverterMessages:
    """Локализованные сообщения для пользователя."""

    def __init__(self, lang="ru"):
        self.lang = lang
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
        if msg is None:
            return key
        return msg.format(**kwargs) if kwargs else msg
