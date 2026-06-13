-- restore_notes.lua
local note_styles = {
    NoteAlert = 'alert',
    NoteInfo = 'info',
    NoteTip = 'tip',
    NoteWarning = 'warning'
}

-- Вспомогательная функция для удаления пробелов в начале и конце строки
local function strip(s)
    return s:match("^%s*(.-)%s*$")
end

function Blocks(blocks)
    local new_blocks = {}
    local i = 1
    local n = #blocks
    
    -- io.stderr:write("Lua filter: restore notes\n")
    -- io.stderr:write("Lua filter: restore notes" .. tostring(style) .. "\n")

    while i <= n do
        local el = blocks[i]
        -- Проверяем, является ли элемент абзацем с нужным кастомным стилем
        -- local style = el.attributes and el.attributes['custom-style']
        
        local style = el.custom_style or el.attributes and el.attributes['custom-style']
    
        -- Вариант Б (Наиболее точный для свежих версий Pandoc):
        -- Проверяем через системное свойство .attr
        if el.attr and el.attr.attributes then
            style = el.attr.attributes['custom-style']
        end

        -- if style then
        --     io.stderr:write("Нашли стиль абзаца: " .. tostring(style) .. "\n")
        -- else
        --     io.stderr:write("Обычный абзац без стиля\n")
        -- end

        if el.t == 'Para' and style and note_styles[style] then
            
            local note_type = note_styles[style]
            local note_paras = {}
            
            -- Собираем ВСЕ идущие подряд абзацы с этим же стилем
            while i <= n and blocks[i].t == 'Para' and blocks[i].attributes and blocks[i].attributes['custom-style'] == style do
                table.insert(note_paras, blocks[i])
                i = i + 1
            end
            
            -- Теперь обрабатываем собранные абзацы заметок
            local title = nil
            local body_parts = {}
            
            for idx, para in ipairs(note_paras) do
                -- Конвертируем абзац AST обратно в Markdown-текст внутри Pandoc
                local md_text = strip(pandoc.utils.stringify(para))
                
                -- Если это самый первый абзац, проверяем, не заголовок ли это.
                -- Pandoc преобразует <text:span text:style-name="Strong..."> в жирный текст, 
                -- но stringify() возвращает чистый текст "Внимание!".
                -- Так как в XML у вас заголовок идет отдельным тегом <text:p>, 
                -- мы можем считать первый абзац заглавием.
                if idx == 1 then
                    title = md_text
                else
                    -- Для остальных абзацев сохраняем их исходное форматирование (курсив и т.д.)
                    -- Чтобы сохранить курсив, переводим элементы Inlines в Markdown
                    local inline_md = pandoc.write(pandoc.Doc(para.content), 'markdown')
                    table.insert(body_parts, strip(inline_md))
                end
            end
            
            local body = table.concat(body_parts, '\n\n')
            
            -- Собираем финальную строку
            local note_markup
            if title and title ~= "" then
                note_markup = string.format('{%% note %s "%s" %%}\n\n%s\n\n{%% endnote %%}', note_type, title, body)
            else
                note_markup = string.format('{%% note %s %%}\n\n%s\n\n{%% endnote %%}', note_type, body)
            end
            
            -- Вставляем как RawBlock во вкусе markdown, чтобы Pandoc не экранировал фигурные скобки
            table.insert(new_blocks, pandoc.RawBlock('markdown', note_markup))
        else
            -- Если элемент не относится к заметкам, просто переносим его как есть
            table.insert(new_blocks, el)
            i = i + 1
        end
    end

    return new_blocks
end