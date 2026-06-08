-- fix-sequence-refs.lua
-- Обрабатывает <text:sequence-ref> из ODT и превращает в удобный для Diplodoc / pandoc-crossref формат

local function is_sequence_ref(inline)
    if inline.t == "RawInline" and inline.format == "odt" then
        return inline.text:match("<text:sequence%-ref")
    end
    return false
end

local function process_sequence_ref(raw)
    -- Извлекаем ref-name и значение
    local ref_name = raw.text:match('text:ref%-name="([^"]+)"')
    local value = raw.text:match(">(%d+)<") or "?"

    if not ref_name then
        return pandoc.Str("[" .. (value) .. "]")  -- fallback
    end

    -- refDrawing0 → fig:fig-0 (или как ты хочешь нумеровать)
    local fig_id = ref_name:match("refDrawing(%d+)")
    if fig_id then
        -- Вариант 1: pandoc-crossref стиль
        return pandoc.Str("[рис. @" .. "fig:fig-" .. fig_id .. "]")
        
        -- Вариант 2: если хочешь просто Markdown-ссылку (как ты просил)
        -- return pandoc.Str("[рис. Рисунок " .. value .. "](./media/some-image.png)")
        -- Но для этого нужно знать, какая именно картинка соответствует refDrawing0 — это сложнее.
    end

    return pandoc.Str("(рис. " .. value .. ")")
end

function RawInline(el)
    if is_sequence_ref(el) then
        return process_sequence_ref(el)
    end
    return el
end

-- На всякий случай — если Pandoc уже превратил в Str
function Str(el)
    local text = el.text
    -- Дополнительная страховка на случай, если sequence-ref "распался"
    text = text:gsub("рис%.%s*", "рис. ")
    return pandoc.Str(text)
end