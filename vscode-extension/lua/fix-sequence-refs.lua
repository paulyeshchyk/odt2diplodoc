-- Карта связей: ref-name (напр. "refDrawing1428") -> src картинки
local ref_to_image_map = {}
local logging = require '../lua/logging'
-- Временные переменные для связывания в первом проходе
local last_seen_ref_name = nil
local last_seen_image_src = nil
local counter = 0
-- Флаг, чтобы не дублировать логи картинок
local logged_images = {}

-- ==========================================
-- ШАГ 1: Сбор карты по уникальным ID (ref-name)
-- ==========================================
local step1_collect = {
    -- Сканируем сырой XML, где бы он ни находился (в списках, абзацах, таблицах)
    RawInline = function(el)
        if el.format == 'opendocument' then
            local ref_name = el.text:match('text:ref%-name="([^"]+)"')
            if ref_name then
                last_seen_ref_name = ref_name

                -- Если картинка распарсилась чуть раньше в этом же блоке
                if last_seen_image_src then
                    ref_to_image_map[ref_name] = last_seen_image_src
                    logging.temp('[ШАГ 1] Связали (Картинка первая): ' .. ref_name .. ' -> ' .. last_seen_image_src)
                    last_seen_image_src = nil
                end
            end
        end
    end,

    -- Сканируем все картинки в документе
    Image = function(img)
        if not logged_images[img.src] then
            counter = counter + 1
            -- logging.temp('[ШАГ 1] Найдена картинка в документе[' .. counter .. ']: ', img.src)
            logged_images[img.src] = true
        end
        if last_seen_ref_name then
            -- Если перед картинкой в XML шел тег с ID
            ref_to_image_map[last_seen_ref_name] = img.src
            logging.temp('[ШАГ 1] Связали (ID первый): ' .. last_seen_ref_name .. ' -> ' .. img.src)
            last_seen_ref_name = nil
        else
            -- Запоминаем картинку, ждем её ID
            last_seen_image_src = img.src
        end
        return img
    end
}

-- ==========================================
-- ШАГ 2: Подмена ссылок в тексте
-- ==========================================
local step2_replace = {
    RawInline = function(el)
        -- Проверяем тег ссылки из ODT XML
        if el.format == 'opendocument' and el.text:match('text:sequence%-ref') then
            local ref_name = el.text:match('text:ref%-name="([^"]+)"')
            local ref_value = el.text:match('>([^<]+)</text:sequence%-ref>')

            if not ref_value then
                ref_value = el.text:match('text:reference%-format="[^"]+">([^<]+)')
            end
            if ref_name and ref_value then
                -- Очищаем номер от пробелов
                ref_value = ref_value:gsub("%s+", "")

                -- Ищем путь к картинке в нашей карте по строгому ID
                local image_src = ref_to_image_map[ref_name]
                if image_src then
                    logging.temp('[УСПЕХ ВТОРОГО ПРОХОДА] Заменили тег ' .. ref_name .. ' на ссылку: ' .. image_src)
                    -- Возвращаем чистый Markdown Link: [1432](Pictures/...)
                    return pandoc.Link({ pandoc.Str(ref_value) }, image_src)
                else
                    logging.temp('[ВНИМАНИЕ] Не нашли картинку для ID ссылки: ' .. tostring(ref_name))
                    return pandoc.Str(ref_value)
                end
            end
            -- Вырезаем пустой XML хлам без образования обратных апострофов
            return pandoc.Str("")
        end
    end
}

-- Возвращаем два изолированных шага через стандартный плоский массив таблиц
return {
    step1_collect,
    step2_replace
}
