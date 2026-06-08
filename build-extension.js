// build-extension.js
const { execSync } = require('child_process');
const path = require('path');

const bumpType = process.argv[2] || 'patch'; // по умолчанию patch

console.log(`Сборка Diplodoc Extension (bump: ${bumpType})...\n`);

try {
    // Увеличиваем версию
    if (bumpType === 'minor') {
        execSync('node vscode-extension/scripts/bump-minor.js', { stdio: 'pipe' });
    } else {
        execSync('node vscode-extension/scripts/bump-version.js', { stdio: 'pipe' });
    }

    // Запускаем полную сборку
    execSync('node vscode-extension/scripts/build.js', {
        stdio: 'pipe'
    });

    console.log('\nГотово!');
} catch (err) {
    let msg = err instanceof Error ? err.message : String(err);
    console.error(`\nОшибка сборки: ${msg}`);
    process.exit(1);
}