// build-extension.js
const { execSync } = require('child_process');
const path = require('path');

console.log('Сборка Diplodoc VS Code Extension...\n');

execSync('node vscode-extension/prepare.js', { stdio: 'inherit' });
console.log('Файлы скопированы\n');

execSync('npm run package', { stdio: 'inherit', cwd: path.join(__dirname, 'vscode-extension') });

console.log('\nГотово!');