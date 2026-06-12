// vscode-extension/prepare.js
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const extDir = __dirname;

console.log('Подготовка расширения...');

// Копируем всю папку python из корня проекта
const srcPython = path.join(rootDir, 'python');
const destPython = path.join(extDir, 'python');

if (fs.existsSync(srcPython)) {
    copyDir(srcPython, destPython);
    console.log('Скопирована папка python (со всеми скриптами)');
} else {
    console.warn('Папка python не найдена!');
}

// Копируем lua-файлы (если нужны)
const srcLua = path.join(rootDir, 'lua');
const destLua = path.join(extDir, 'lua');

if (fs.existsSync(srcLua)) {
    copyDir(srcLua, destLua);
    console.log('Скопирована папка lua');
} else {
    console.warn('Папка lua не найдена (пропускаем)');
}

function copyDir(src, dest) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
    const entries = fs.readdirSync(src, { withFileTypes: true });
    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        if (entry.isDirectory()) {
            copyDir(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}