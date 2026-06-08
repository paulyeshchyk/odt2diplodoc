-- no-img-size.lua
function Image (img)
    -- Просто возвращаем изображение, но с очищенными атрибутами
    img.attr = pandoc.Attr{}
    return img
end