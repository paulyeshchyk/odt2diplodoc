// vscode-extension/prepare.js
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const luaDir = path.join(rootDir, 'lua');
const extDir = __dirname;

console.log('Подготовка расширения...');

// Копируем diplodoc_converter
const srcPython = path.join(rootDir, 'diplodoc_converter');
const destPython = path.join(extDir, 'python', 'diplodoc_converter');

if (fs.existsSync(srcPython)) {
    copyDir(srcPython, destPython);
    console.log('Скопирован diplodoc_converter');
} else {
    console.warn('Папка diplodoc_converter не найдена!');
}

// Копируем .lua файлы из корня
console.log('Подготовка lua...');
const luaFiles = fs.readdirSync(luaDir).filter(f => f.endsWith('.lua'));
if (luaFiles.length > 0) {
    const destLua = path.join(extDir, 'lua');
    if (!fs.existsSync(destLua)) fs.mkdirSync(destLua);

    luaFiles.forEach(file => {
        fs.copyFileSync(path.join(luaDir, file), path.join(destLua, file));
    });
    console.log(`Скопировано ${luaFiles.length} lua-файлов`);
} else {
    console.warn('lua файлы не найдены');
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