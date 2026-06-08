// vscode-extension/scripts/build.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const extRoot = path.resolve(__dirname, '..');
const buildDir = path.join(extRoot, 'build');

console.log('Сборка Diplodoc VS Code Extension...\n');

// Создаём папку build
if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir, { recursive: true });
}

// 1. Подготовка файлов
console.log('Копирование python и lua...');
execSync('node prepare.js', { stdio: 'inherit', cwd: extRoot });

// 2. Сборка VSIX
console.log('\nУпаковка расширения...');
const result = execSync('npm run package:force', {
    stdio: 'pipe',
    cwd: extRoot,
    encoding: 'utf8'
});

console.log(result);

// 3. Перемещаем .vsix в build/
const vsixFiles = fs.readdirSync(extRoot).filter(f => f.endsWith('.vsix'));
if (vsixFiles.length > 0) {
    const latestVsix = vsixFiles[vsixFiles.length - 1];
    const sourcePath = path.join(extRoot, latestVsix);
    const targetPath = path.join(buildDir, latestVsix);

    fs.renameSync(sourcePath, targetPath);
    console.log(`\nГотово! Файл сохранён в:\n   ${targetPath}`);
} else {
    console.error('.vsix файл не найден');
}