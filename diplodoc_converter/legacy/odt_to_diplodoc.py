import os
import re
import shutil
import subprocess
import yaml


def convert_odt_to_diplodoc(odt_path, output_dir):
    temp_md = "temp_full_doc.md"
    temp_media_dir = "temp_images"

    # Шаг 1: Конвертация через Pandoc и извлечение картинок
    print("Конвертация ODT в Markdown с извлечением медиа...")
    try:
        subprocess.run(["pandoc", odt_path, "-f", "odt", "-t", "markdown_strict+pipe_tables+backtick_code_blocks", "--filter=pandoc-crossref", "--lua-filter=no-img-size.lua", "--extract-media=" + temp_media_dir, "-o", temp_md], check=True)
    except FileNotFoundError:
        print("Ошибка: Убедитесь, что Pandoc установлен и добавлен в PATH.")
        return

    # Читаем полученный Markdown
    with open(temp_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Шаг 2: Разбор контента по заголовкам (сейчас настроено на заголовок 1 уровня # )
    # При необходимости регулярку можно усложнить для поддержки h2 (## )
    sections = re.split(r"^(?=# )", content, flags=re.MULTILINE)

    # Структура для корневого оглавления проекта
    root_toc_items = []

    for idx, section in enumerate(sections):
        if not section.strip():
            continue

        lines = section.strip().split("\n")
        raw_title = lines[0].replace("#", "").strip()

        # Генерируем безопасное имя папки из заголовка
        folder_name = f"{idx:02d}_" + re.sub(r"[^\w\s-]", "", raw_title).strip().lower().replace(" ", "_")
        chapter_dir = os.path.join(output_dir, folder_name)
        os.makedirs(chapter_dir, exist_ok=True)

        print(f"Обработка главы: {raw_title} -> папка {folder_name}")

        # Текст главы без заголовка первого уровня
        chapter_text = "\n".join(lines[1:])

        # Шаг 3: Работа с изображениями для этой конкретной главы
        # Текст главы без заголовка первого уровня
        chapter_text = "\n".join(lines[1:])

        # Шаг 3: Находим ВСЕ картинки в тексте главы
        # Ищем как Markdown синтаксис ![](...), так и HTML теги <img src="..." />
        img_pattern = r'(?:!\[.*?\]\(|<img\s+[^>]*src=")(temp_images/[^"\)]+)'
        images_found = re.findall(img_pattern, chapter_text)

        chapter_images_dir = os.path.join(chapter_dir, "media")

        if images_found:
            os.makedirs(chapter_images_dir, exist_ok=True)

            for full_src_path in images_found:
                # Извлекаем только имя файла (например, 10000001000001A900000202499FD308EE27DB46.png)
                img_name = os.path.basename(full_src_path)
                dest_img_path = os.path.join(chapter_images_dir, img_name)

                # Проверяем, существует ли физический файл во временной папке
                # (Pandoc мог положить его в temp_images/media/ или temp_images/Pictures/)
                if os.path.exists(full_src_path):
                    shutil.copy(full_src_path, dest_img_path)

                    # Шаг 4: Заменяем старую ссылку/тег на чистый Markdown для Diplodoc
                    # Этот блок заменит и весь HTML-тег <img>, и Markdown-ссылку на правильный относительный путь

                    # 1. Если это был HTML-тег <img>, заменяем его целиком
                    html_tag_pattern = rf'<img\s+[^>]*src="{re.escape(full_src_path)}"[^>]*>'
                    if re.search(html_tag_pattern, chapter_text):
                        chapter_text = re.sub(html_tag_pattern, f"![image](images/{img_name})", chapter_text)

                    # 2. Если это была стандартная Markdown ссылка
                    chapter_text = chapter_text.replace(full_src_path, f"images/{img_name}")
                else:
                    print(f"Предупреждение: Файл {full_src_path} не найден на диске.")

        # Шаг 4: Генерация файлов для Diplodoc

        # 1. index.md
        with open(os.path.join(chapter_dir, "index.md"), "w", encoding="utf-8") as f_md:
            f_md.write(chapter_text.strip())

        # 2. index.yaml
        index_yaml_content = {"title": raw_title, "meta": {"title": raw_title}}
        with open(os.path.join(chapter_dir, "index.yaml"), "w", encoding="utf-8") as f_idx:
            yaml.dump(index_yaml_content, f_idx, allow_unicode=True, sort_keys=False)

        # 3. toc.yaml (для самой главы, ссылается на свой же index.md)
        toc_yaml_content = {"title": raw_title, "items": [{"name": raw_title, "href": "index.md"}]}
        with open(os.path.join(chapter_dir, "toc.yaml"), "w", encoding="utf-8") as f_toc:
            yaml.dump(toc_yaml_content, f_toc, allow_unicode=True, sort_keys=False)

        # Добавляем главу в корень глобального оглавления
        root_toc_items.append({"name": raw_title, "href": f"{folder_name}/toc.yaml"})

    # Шаг 5: Создаем корневой toc.yaml в output_dir
    root_toc = {"title": "Документация", "items": root_toc_items}
    with open(os.path.join(output_dir, "toc.yaml"), "w", encoding="utf-8") as f_root_toc:
        yaml.dump(root_toc, f_root_toc, allow_unicode=True, sort_keys=False)

    # Очистка временных файлов
    if os.path.exists(temp_md):
        os.remove(temp_md)
    if os.path.exists(temp_media_dir):
        shutil.rmtree(temp_media_dir)
    print("\nКонвертация успешно завершена!")


# Пример запуска:
# convert_odt_to_diplodoc("manual.odt", "./diplodoc_project")
