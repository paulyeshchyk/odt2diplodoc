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
        return pandoc.Str("[" .. (value) .. "]") 
    end

    -- refDrawing0 fig:fig-0
    local fig_id = ref_name:match("refDrawing(%d+)")
    if fig_id then
        return pandoc.Str("[рис. @" .. "fig:fig-" .. fig_id .. "]")
    end

    return pandoc.Str("(рис. " .. value .. ")")
end

function RawInline(el)
    io.stderr:write("Processing string: " .. el.text .. "\n")
    if is_sequence_ref(el) then
        return process_sequence_ref(el)
    end
    return el
end

function Str(el)

    local text = el.text

    text = text:gsub("рис%.%s*", "рис. ")
    return pandoc.Str(text)
end